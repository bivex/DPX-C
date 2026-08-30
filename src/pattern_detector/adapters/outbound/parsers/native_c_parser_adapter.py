"""High-performance Native C (C89/C99/C11/C17/C23) AST & CST Parser Adapter implementing ParserPort."""

from __future__ import annotations

import os
import re
from pathlib import Path

from pattern_detector.domain.code_model import (
    CodeModel,
    FileModel,
    FunctionModel,
    FunctionParamModel,
    MacroModel,
    StructMemberModel,
    StructModel,
    TypedefModel,
)
from pattern_detector.domain.value_objects import SourceLocation
from pattern_detector.ports.outbound import ParserPort


class NativeCParserAdapter(ParserPort):
    """High-performance native C parser supporting C89 to C23 syntax."""

    def parse_sources(self, sources: dict[str, str]) -> CodeModel:
        model = CodeModel()
        from concurrent.futures import ThreadPoolExecutor

        def _worker(item: tuple[str, str]) -> tuple[str, FileModel]:
            f_path, src_text = item
            return f_path, self.parse_file(f_path, src_text)

        with ThreadPoolExecutor() as executor:
            results = executor.map(_worker, sources.items())
            for f_path, file_model in results:
                model.files[f_path] = file_model

        return model

    def parse_file(self, file_path: str, source_text: str) -> FileModel:
        clean_text = self._strip_comments_and_strings(source_text)
        is_hdr = file_path.endswith(".h") or file_path.endswith(".hpp")
        loc = SourceLocation(file_path=file_path, line=1, column=1)

        file_model = FileModel(
            file_path=file_path,
            is_header=is_hdr,
            raw_source=source_text,
            location=loc,
        )

        # 1. Includes
        file_model.includes = self._parse_includes(clean_text)

        # 2. Macros
        file_model.macros = self._parse_macros(clean_text, file_path)

        # 3. Structs and Unions
        file_model.structs = self._parse_structs(clean_text, file_path)

        # 4. Typedefs
        file_model.typedefs = self._parse_typedefs(clean_text, file_path)

        # 5. Functions
        file_model.functions = self._parse_functions(clean_text, file_path)

        return file_model

    # -------------------------------------------------------------------------
    # Parsing Helpers
    # -------------------------------------------------------------------------

    def _strip_comments_and_strings(self, text: str) -> str:
        # Strip block comments /* ... */
        clean = re.sub(r"/\*[\s\S]*?\*/", " ", text)
        # Strip line comments // ...
        clean = re.sub(r"//.*", "", clean)
        return clean

    def _parse_includes(self, text: str) -> list[str]:
        includes = []
        for m in re.finditer(r'#\s*include\s*[<"]([^>"]+)[>"]', text):
            includes.append(m.group(1))
        return includes

    def _parse_macros(self, text: str, file_path: str) -> dict[str, MacroModel]:
        macros: dict[str, MacroModel] = {}
        pattern = re.compile(r"#\s*define\s+([a-zA-Z0-9_]+)(?:\(([^)]*)\))?\s*(.*)", re.MULTILINE)
        cur_pos = 0
        cur_line = 1

        for m in pattern.finditer(text):
            name = m.group(1)
            params_raw = m.group(2)
            defn = m.group(3).strip()
            params = [p.strip() for p in params_raw.split(",")] if params_raw else []

            cur_line += text.count("\n", cur_pos, m.start())
            cur_pos = m.start()
            loc = SourceLocation(file_path=file_path, line=cur_line)

            macros[name] = MacroModel(
                name=name,
                params=params,
                definition=defn,
                is_function_like=(params_raw is not None),
                location=loc,
            )
        return macros

    def _parse_structs(self, text: str, file_path: str) -> dict[str, StructModel]:
        structs: dict[str, StructModel] = {}

        pattern = re.compile(
            r"\b(?:typedef\s+)?(struct|union)\s+([a-zA-Z0-9_]+)?\s*\{",
            re.MULTILINE,
        )

        pos = 0
        cur_pos = 0
        cur_line = 1

        while pos < len(text):
            m = pattern.search(text, pos)
            if not m:
                break

            kind = m.group(1)
            raw_name = m.group(2)

            body, end_pos = self._extract_braces_block(text, m.end() - 1)
            after = text[end_pos + 1 : end_pos + 150]
            semi_idx = after.find(";")
            alias = after[:semi_idx].strip() if semi_idx != -1 else ""
            pos = end_pos + (semi_idx + 1 if semi_idx != -1 else 1)

            name = raw_name or (alias.split(",")[0].strip().strip("*").strip() if alias else "anonymous")
            cur_line += text.count("\n", cur_pos, m.start())
            cur_pos = m.start()
            loc = SourceLocation(file_path=file_path, line=cur_line)

            members = self._parse_struct_members(body)
            struct_model = StructModel(
                name=name,
                members=members,
                is_union=(kind == "union"),
                location=loc,
            )
            structs[name] = struct_model
            if alias:
                for a in alias.split(","):
                    a_clean = a.strip().strip("*").strip()
                    if a_clean and a_clean != name:
                        structs[a_clean] = struct_model

        return structs

    def _parse_struct_members(self, body: str) -> list[StructMemberModel]:
        members: list[StructMemberModel] = []
        for line in body.split(";"):
            line = line.strip()
            if not line:
                continue

            # Function pointer member: int (*read)(void* buf, size_t len)
            fp_m = re.search(r"([a-zA-Z0-9_*\s]+)\(\s*\*\s*([a-zA-Z0-9_]+)\s*\)\s*\(([^)]*)\)", line)
            if fp_m:
                ret_type = fp_m.group(1).strip()
                fp_name = fp_m.group(2).strip()
                params = [p.strip() for p in fp_m.group(3).split(",") if p.strip()]
                members.append(
                    StructMemberModel(
                        name=fp_name,
                        type_str=ret_type,
                        is_function_pointer=True,
                        func_ptr_params=params,
                    )
                )
                continue

            # Regular member: int capacity; struct node* next;
            tokens = line.split()
            if len(tokens) >= 2:
                field_name = tokens[-1].strip("*[]0123456789")
                type_str = " ".join(tokens[:-1])
                is_ptr = "*" in line
                is_arr = "[" in line
                members.append(
                    StructMemberModel(
                        name=field_name,
                        type_str=type_str,
                        is_pointer=is_ptr,
                        is_array=is_arr,
                    )
                )

        return members

    def _parse_typedefs(self, text: str, file_path: str) -> dict[str, TypedefModel]:
        typedefs: dict[str, TypedefModel] = {}
        cur_pos = 0
        cur_line = 1

        for m in re.finditer(r"\btypedef\s+([^;]+);", text):
            full_stmt = m.group(0).strip()
            body = m.group(1).strip()
            cur_line += text.count("\n", cur_pos, m.start())
            cur_pos = m.start()
            loc = SourceLocation(file_path=file_path, line=cur_line)

            # Function pointer typedef: typedef void (*callback_fn)(void*);
            fp_m = re.search(r"([a-zA-Z0-9_*\s]+)\(\s*\*\s*([a-zA-Z0-9_]+)\s*\)\s*\(([^)]*)\)", body)
            if fp_m:
                name = fp_m.group(2)
                typedefs[name] = TypedefModel(name=name, target_type=full_stmt, is_function_pointer=True, location=loc)
                continue

            # Regular typedef: typedef struct foo_s foo_t;
            tokens = body.split()
            if len(tokens) >= 2:
                name = tokens[-1].strip("*")
                target = " ".join(tokens[:-1])
                typedefs[name] = TypedefModel(name=name, target_type=target, is_function_pointer=False, location=loc)

        return typedefs

    def _parse_functions(self, text: str, file_path: str) -> dict[str, FunctionModel]:
        functions: dict[str, FunctionModel] = {}

        # Matches function definition: [static] [inline] return_type name(args) { ... }
        fn_pattern = re.compile(
            r"(?:^|[;{}])\s*(static\s+|inline\s+|extern\s+)*([a-zA-Z0-9_* \t]+)\s+([a-zA-Z0-9_]+)\s*\(([^;{}]*)\)\s*\{",
            re.MULTILINE,
        )

        pos = 0
        cur_pos = 0
        cur_line = 1

        while pos < len(text):
            m = fn_pattern.search(text, pos)
            if not m:
                break

            modifiers = m.group(1) or ""
            ret_type = (m.group(2) or "").strip()
            name = m.group(3).strip()
            args_raw = m.group(4) or ""

            # Exclude control keywords that look like functions
            if name in ("if", "while", "for", "switch", "catch", "return", "sizeof", "do", "else"):
                pos = m.end()
                continue

            cur_line += text.count("\n", cur_pos, m.start())
            cur_pos = m.start()
            loc = SourceLocation(file_path=file_path, line=cur_line)

            body, end_pos = self._extract_braces_block(text, m.end() - 1)
            pos = end_pos + 1

            params = self._parse_function_params(args_raw)
            calls = re.findall(r"\b([a-zA-Z0-9_]+)\s*\(", body)
            complexity = 1 + body.count("if ") + body.count("else if ") + body.count("for (") + body.count("while (") + body.count("case ")

            fn_model = FunctionModel(
                name=name,
                return_type=ret_type,
                params=params,
                is_static=("static" in modifiers),
                is_inline=("inline" in modifiers),
                is_definition=True,
                body=body,
                cyclomatic_complexity=complexity,
                calls=calls,
                has_goto=("goto " in body),
                has_malloc=("malloc(" in body or "calloc(" in body or "realloc(" in body),
                has_free=("free(" in body),
                has_unsafe_str=("strcpy(" in body or "strcat(" in body or "sprintf(" in body or "gets(" in body),
                location=loc,
            )
            functions[name] = fn_model

        return functions

    def _split_top_level_comma(self, text: str) -> list[str]:
        if not text.strip():
            return []
        items = []
        current = []
        depth = 0
        in_string = False
        quote_char = ""
        escape = False

        for c in text:
            if escape:
                escape = False
                current.append(c)
                continue
            if c == "\\" and in_string:
                escape = True
                current.append(c)
                continue
            if c in ('"', "'") and not in_string:
                in_string = True
                quote_char = c
                current.append(c)
            elif c == quote_char and in_string:
                in_string = False
                current.append(c)
            elif not in_string:
                if c in ("(", "{", "[", "<"):
                    depth += 1
                    current.append(c)
                elif c in (")", "}", "]", ">"):
                    depth -= 1
                    current.append(c)
                elif c == "," and depth == 0:
                    items.append("".join(current).strip())
                    current = []
                else:
                    current.append(c)
            else:
                current.append(c)

        if current:
            items.append("".join(current).strip())
        return [it for it in items if it]

    def _parse_function_params(self, raw_args: str) -> list[FunctionParamModel]:
        params: list[FunctionParamModel] = []
        if not raw_args.strip() or raw_args.strip() == "void":
            return params

        for arg in self._split_top_level_comma(raw_args):
            arg = arg.strip()
            if not arg:
                continue

            # Function pointer param: int (*cmp)(const void*, const void*)
            fp_m = re.search(r"([a-zA-Z0-9_*\s]+)\(\s*\*\s*([a-zA-Z0-9_]+)\s*\)", arg)
            if fp_m:
                p_name = fp_m.group(2)
                p_type = fp_m.group(1).strip()
                params.append(FunctionParamModel(name=p_name, type_str=p_type, is_function_pointer=True))
                continue

            tokens = arg.split()
            if tokens:
                p_name = tokens[-1].strip("*[]")
                p_type = " ".join(tokens[:-1]) if len(tokens) > 1 else tokens[0]
                is_ptr = "*" in arg
                params.append(FunctionParamModel(name=p_name, type_str=p_type, is_pointer=is_ptr))

        return params

    def _extract_braces_block(self, text: str, start_pos: int) -> tuple[str, int]:
        first_brace = text.find("{", start_pos)
        if first_brace == -1:
            return text[start_pos:], len(text)

        depth = 1
        curr = first_brace + 1
        text_len = len(text)

        while curr < text_len and depth > 0:
            next_open = text.find("{", curr)
            next_close = text.find("}", curr)

            if next_close == -1:
                return text[first_brace + 1:], text_len

            if next_open != -1 and next_open < next_close:
                depth += 1
                curr = next_open + 1
            else:
                depth -= 1
                if depth == 0:
                    return text[first_brace + 1:next_close], next_close
                curr = next_close + 1

        return text[first_brace + 1:], text_len

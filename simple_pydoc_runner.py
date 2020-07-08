import argparse
import ast
import os

#got base code from https://stackoverflow.com/questions/44698193/how-to-get-a-list-of-classes-and-functions-from-a-python-file-without-importing

def get_function_info(function_node, level, method=False):
    if method: 
        typ = "Method" 
    else : 
        typ = "Function"

    string = ("#" * (level + 1)) + " {typ} {name}()\n\n".format(typ=typ, name=function_node.name)

    docstr = ast.get_docstring(function_node)
    if docstr is not None:
        string += docstr + "\n\n"

    args = [arg.arg for arg in function_node.args.args if arg.arg != 'self']
    if len(args) > 0:
        args = str(args).replace('[', '').replace(']', '').replace("'", '')
        string += "* Arguments: {}\n\n".format(args)
    else:
        string += "* No Arguments.\n\n"


    return string

def get_class_info(class_node, level):
    string = ("#" * (level + 1)) + " Class {}\n\n".format(class_node.name)

    docstr = ast.get_docstring(class_node)
    if docstr is not None:
        string += docstr + "\n\n"

    methods = [n for n in class_node.body if isinstance(n, ast.FunctionDef)]

    for m in methods:
        string += get_function_info(m, 1, method=True)
    if len(methods) == 0:
        string += "No methods.\n\n"

    return string

def generate_doc_string_for_file(file_path, output_file):
    with open(file_path, 'r') as input_file:
        node = ast.parse(input_file.read())

        functions = [n for n in node.body if isinstance(n, ast.FunctionDef)]
        classes = [n for n in node.body if isinstance(n, ast.ClassDef)]

        output = "# File {}\n\n".format(os.path.basename(file_path))
        for function in functions:
            output += get_function_info(function, 1)

        for cls in classes:
            output += get_class_info(cls, 1)

        with open(output_file.replace(".py", ".md"), "w+") as output_file:
            output_file.write(output)

def generate_doc_string_for_dir(dir_path, output_path):
    for root, dirs, files in os.walk(dir_path): 
        for file in files:
            if (file.endswith(".py") 
                and not "__" in file):
                input_file = os.path.join(root, file)
                output_file = os.path.join(output_path, file)
                generate_doc_string_for_file(input_file, output_file)

        for dir_ in dirs:
            if not "__" in dir_:
                input_dir = os.path.join(root, dir_)
                output_dir = os.path.join(output_path, dir_)
                if not os.path.exists(output_dir): os.makedirs(output_dir)
                generate_doc_string_for_dir(input_dir, output_dir)

        break

def main():
    parser = argparse.ArgumentParser(description='Generate python documentation for a file or a folder.')
    parser.add_argument('input_file', help='Input file or folder.', metavar='INPUT_FILE_OR_FOLDER')
    parser.add_argument('--output', help='Output directory, by default this program outputs to a folder called "docs".', action='store')

    args = parser.parse_args()

    output = ""
    if args.output is None:
        os.makedirs("doc")
        output = "doc"
    else:
        output = args.output

    if os.path.isdir(args.input_file):
        generate_doc_string_for_dir(args.input_file, output)
    else:
        generate_doc_string_for_file(args.input_file, os.path.join(output, os.path.basename(args.input_file)))

main()

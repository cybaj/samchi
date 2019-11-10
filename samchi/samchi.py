import os
import argparse

_spec_path = "./sample.txt"
_target_path = "."
_project_name = ""
_target_os = "linux"
_hierarchy_text_type = "base"
_hierarchy_text_type_blank = "    "
_hierarchy_text_type_blank_length = len(_hierarchy_text_type_blank)
_hierarchy_text_type_dir_escape = "/"
_hierarchy_text_type_script_extension = ".py"
_ignores = ['\r', '\n']

configuration = {
        "spec_path": _spec_path,
        "target_path": _target_path,
        "project_path": "",
        "project_name": _project_name,
        "target_os": _target_os,
        "hierarchy_text_type": _hierarchy_text_type,
        "hierarchy_text_type_blank": _hierarchy_text_type_blank,
        "hierarchy_text_type_blank_length": _hierarchy_text_type_blank_length,
        "hierarchy_text_type_dir_escape": _hierarchy_text_type_dir_escape,
        "hierarchy_text_type_script_extension": _hierarchy_text_type_script_extension
}

def set_root_path(target_path):
    root_path = os.path.join(target_path, _project_name)
    return root_path

def read_spec(spec_path, ignores):
    spec_path = os.path.join(spec_path)
    lines = []
    try:
        f = open(spec_path, 'r', encoding='utf-8')
    except FileNotFoundError as e:
        print(e)
        import sys
        sys.exit()
    while not f.closed:
        line = f.readline()
        if not line:
            f.close()
        elif not line in ignores: 
            count = 0
            for ignore in ignores:
                if line.endswith(ignore):
                    count += 1
            lines.append(line[:-count])
        else:
            continue
    return lines

def touch(path, is_init=False):
    with open(path, 'a'):
        if is_init:
            pass
        os.utime(path, None)

class Spec:
    def __init__(self, lines, configuration):
        self.configuration = configuration
        self._lines = lines
        self.base_path = configuration['project_path']

    def set_project_directory(self):
        configuration = self.configuration
        lines = self._lines
        current_path = os.path.join(self.base_path, lines[0][:-1])
        os.mkdir(current_path)
        count_stack = [0]
        history = [(0, current_path)]
        for line in lines[1:]:
            count = 0 
            is_dir = False
            is_script = False
            lastname = ""
            while line.startswith(configuration['hierarchy_text_type_blank']):
                line = line[configuration['hierarchy_text_type_blank_length']:]
                count += 1
            if line.endswith(configuration['hierarchy_text_type_dir_escape']):
                lastname = line[:-len(configuration['hierarchy_text_type_dir_escape'])]
                is_dir = True
            elif line.endswith(configuration['hierarchy_text_type_script_extension']):
                lastname = line
                is_script = True
            if not count == count_stack[-1] and is_dir:
                current_path = os.path.join(current_path, lastname)
                os.mkdir(current_path)
                history.append((count, current_path))
            elif is_dir:
                current_path = os.path.join(current_path, '..', lastname)
                os.mkdir(current_path)
                history.append((count, current_path))
            elif is_script:
                parent_dir_count = count - 1
                for dir_count, dir_path in history:
                    if parent_dir_count == dir_count:
                        current_path = dir_path
                os.mknod(current_path+'/'+lastname)
            if is_dir:
                count_stack.append(count)
         
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--spec', metavar="spec_path", default=os.path.dirname(os.path.realpath(__file__))+'/example/sample.txt', dest="spec_path")
    parser.add_argument('target_path', metavar="project_root_path")
    args = parser.parse_args()
    configuration['spec_path'] = args.spec_path
    configuration['target_path'] = args.target_path

    project_root_path = set_root_path(configuration['target_path'])
    configuration['project_path'] = project_root_path
    hierarchy_textLines = read_spec(configuration['spec_path'], _ignores)
    spec = Spec(hierarchy_textLines, configuration)
    spec.set_project_directory()

if __name__ == "__main__" :
    main()


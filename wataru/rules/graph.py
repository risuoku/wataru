from wataru.rules.models import (
    EmptyFile,
    EmptyDirectory,
    ProjectRoot,
)


class RuleGraph:
    def __init__(self, graph_dict):
        self._gd = graph_dict.get('body') or graph_dict
        self._project = None

    def build(self):
        project_name = self._gd['name']
        project_rootdir = self._gd['rootdir']
        project_children = self._gd.get('children')
        project_venv = self._gd.get('virtualenv', True)

        self._project = ProjectRoot (
            rootdir = project_rootdir,
            name = project_name,
            virtualenv = project_venv
        )
        if project_children is None:
            return self # プロジェクトが空なので終了

        self._process_recursive(self._project, project_children)
        return self

    def _process_recursive(self, node, d_children):
        for dc in d_children:
            if dc['type'] == 'file':
                f = EmptyFile(parent=node, name=dc['name'])
                node.add_node(f)
            elif dc['type'] == 'directory':
                d = EmptyDirectory(parent=node, name=dc['name'])
                if 'children' in dc:
                    self._process_recursive(d, dc['children'])
                node.add_node(d)
            else:
                raise ValueError('invalid node type')

    @property
    def project(self):
        return self._project


def get_by_theme(tm):
    return RuleGraph(tm.config).build()

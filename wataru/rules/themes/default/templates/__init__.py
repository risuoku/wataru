import jinja2
import wataru.settings as settings

env = jinja2.Environment (
    loader = jinja2.FileSystemLoader(settings.WATARU_TEMPLATE_DIR_PATH, encoding='utf-8')
)

def get(path):
    return env.get_template(path)

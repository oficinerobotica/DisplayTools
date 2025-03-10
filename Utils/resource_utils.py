from os import path

resources_path = path.join(path.dirname(path.realpath(__file__)), '..', 'Resources')
icons_path = path.join(resources_path, 'Icons')
ui_path = path.join(resources_path, 'UI')

def iconPath(name):
    from os import path
    f = path.join(path.dirname(path.dirname(path.realpath(__file__))), 'Resources', 'Icons', name)
    return f

def uiPath(name):
    f = path.join(ui_path, name)

    return f
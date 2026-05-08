import pkgutil
import importlib

def find_class_in_package(package_name, class_name):
    package = importlib.import_module(package_name)
    for loader, module_name, is_pkg in pkgutil.walk_packages(package.__path__, package.__name__ + '.'):
        try:
            module = importlib.import_module(module_name)
            if hasattr(module, class_name):
                print(f"Found {class_name} in {module_name}")
        except:
            continue

if __name__ == "__main__":
    # This might be slow
    print("Searching for create_react_agent...")
    find_class_in_package('langchain_classic', 'create_react_agent')
    find_class_in_package('langchain', 'create_react_agent')

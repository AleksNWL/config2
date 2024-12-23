import json
import importlib.metadata
from pathlib import Path
import sys


class DependencyVisualizer:
    def __init__(self, config_path):
        self.config = self.load_config(config_path)
        self.package_name = self.config["package_name"]
        self.output_file = self.config["output_file"]
        self.max_depth = self.config["max_depth"]

    def load_config(self, config_path):
        with open(config_path, 'r') as f:
            return json.load(f)

    def get_dependencies(self, package, depth=0):
        if depth >= self.max_depth:
            return {}

        try:
            dist = importlib.metadata.distribution(package)
            requires = dist.requires or []
        except importlib.metadata.PackageNotFoundError:
            print(f"Warning: Package '{package}' not found.")
            return {}

        dependencies = {}
        for req in requires:
            dep_name = req.split()[0]
            if dep_name not in dependencies:
                dependencies[dep_name] = self.get_dependencies(dep_name, depth + 1)

        return dependencies

    def generate_plantuml(self, dependencies):
        lines = ["@startuml"]
        processed = set()

        def add_edges(parent, deps):
            for dep, subdeps in deps.items():
                if dep not in processed:
                    lines.append(f'"{parent}" -> "{dep}";')
                    processed.add(dep)
                    add_edges(dep, subdeps)

        add_edges(self.package_name, dependencies[self.package_name])
        lines.append("@enduml")
        return "\n".join(lines)

    def save_output(self, content):
        with open(self.output_file, 'w') as f:
            f.write(content)

    def visualize(self):
        dependencies = {self.package_name: self.get_dependencies(self.package_name)}
        plantuml_code = self.generate_plantuml(dependencies)
        self.save_output(plantuml_code)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python visualizer.py <config_path>")
        sys.exit(1)

    config_path = sys.argv[1]

    if not Path(config_path).exists():
        print(f"Error: Config file '{config_path}' not found.")
        sys.exit(1)

    try:
        visualizer = DependencyVisualizer(config_path)
        visualizer.visualize()
        print(f"Dependency diagram has been saved to {visualizer.output_file}.")
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

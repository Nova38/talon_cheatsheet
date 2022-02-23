

from talon import Module, actions, registry
import json

from pathlib import Path

# from talon.scripting import context
from rich import print

# from user.knausj_talon.code.code import commands_updated

from dataclass_csv import DataclassWriter
from dataclasses import asdict, dataclass, field


user_registry_list = ['user.letter', 'user.number_key', 'user.modifier_key',
                      'user.special_key', 'user.symbol_key', 'user.arrow_key',
                      'user.punctuation', 'user.function_key']



@dataclass(frozen=True)
class Command_Item:
    name: str
    command: str
    latex_row: str = ""
    alt_names: list[str] = field(default_factory=list)
    os: str = ""

    def __eq__(self, __o: object) -> bool:
        return self.command == __o.command

    def __post_init__(self):
        name = latex_sanitizer(self.name)
        command = latex_sanitizer(self.command)

        object.__setattr__(self, 'latex_row',
                           f'\\Row{{Say={name}, Command={command}}}')




@dataclass
class Context_List:
    name: str
    pretty_name: str = ""
    os: str = ""
    latex: str = ""
    raw_commands: list[dict] = field(default_factory=list)
    commands: list[Command_Item] = field(default_factory=list)

    def __post_init__(self):
        self.pretty_name, self.os = get_pretty_context_name(self.name)
        self.commands = [Command_Item(name=command.rule.rule, command=command.target.code, os=self.os)
                         for command in registry.contexts[self.name].commands.values()
                         ]

        for command in self.commands:
            self.latex += command.latex_row + "\n"




@dataclass
class Registry_List:
    name: str
    pretty_name: str = ""
    registry: str = ""
    # os: str = ""
    latex: str = ""
    commands: list[Command_Item] = field(default_factory=list)

    def __post_init__(self):
        self.registry = self.name.split(".")[0]
        self.pretty_name = self.name.split(".")[1]

        self.commands = [Command_Item(name=name, command=command)
                         for name, command in registry.lists[self.name][0].items()]

        for command in self.commands:
            self.latex += command.latex_row + "\n"


@dataclass
class command_list:
    user_registry:  field(default_factory=list([Command_Item]))
    contexts:       field(default_factory=list([Context_List]))


def latex_sanitizer(string: str):
    symbol_map = {'\'': '\\textquotesingle{}',
                  '"': '\\textquotedbl{}',
                  '`': '\\textasciigrave{}',
                  '^': '\\textasciicircum{}',
                  '~': '\\textasciitilde{}',
                  '<': '\\textless{}',
                  '>': '\\textgreater{}',
                  '|': '\\textbar{}',
                  '\\': '\\textbackslash{}',
                  '{': '\\{',
                  '}': '\\}',
                  '$': '\\$',
                  '&': '\\&',
                  '#': '\\#',
                  '_': '\\_',
                  '%': '\\%'}
    translation_table = str.maketrans(symbol_map)

    return string.translate(translation_table)


def get_pretty_context_name(name: str):
    # The logic here is intended to only print from talon files that have actual voice commands.
    splits = name.split(".")
    index = -1

    os_name = "all"

    if "mac" in name:
        os_name = "mac"
    if "win" in name:
        os_name = "win"
    if "linux" in name:
        os_name = "linux"

    if "talon" in splits[index]:
        index = -2
        short_name = splits[index].replace("_", " ")
    else:
        short_name = splits[index].replace("_", " ")

    if "mac" == short_name or "win" == short_name or "linux" == short_name:
        index = index - 1
        short_name = splits[index].replace("_", " ")

    return (short_name, os_name)


mod = Module()


@mod.action_class
class user_actions:
    def export_cheatsheet():
        """Print out a sheet of talon commands"""

        all_commands = command_list(
            user_registry=[Registry_List(name=reg_name)
                           for reg_name in user_registry_list],
            contexts=[Context_List(name=name) for name in registry.contexts]
        )

        # PATHS

        base_dir = Path(__file__).parent.absolute()
        base_csv_dir = base_dir / 'csv'
        base_latex_tables_dir = base_dir / 'latex'/'tables'

        json_path = base_dir / 'cheatsheet.json'

        csv_reg_dir = base_csv_dir / 'user_registry'
        csv_reg_dir.mkdir(exist_ok=True, parents=True)

        csv_ctx_dir = base_csv_dir / 'contexts'
        csv_ctx_dir.mkdir(exist_ok=True, parents=True)

        latex_tables_dir_reg = base_latex_tables_dir / 'user_registry'
        latex_tables_dir_reg.mkdir(exist_ok=True, parents=True)

        latex_tables_dir_ctx = base_latex_tables_dir / 'contexts'
        latex_tables_dir_ctx.mkdir(exist_ok=True, parents=True)

        # Json File Genoration
        json_path.write_text(json.dumps(asdict(all_commands), indent=4))

        # CSV File Generation
        for user_registry in all_commands.user_registry:
            csv_file = csv_reg_dir / f'{user_registry.pretty_name}.csv'
            csv_file.touch(exist_ok=True)
            with open(csv_file, "w", newline='') as f:
                w = DataclassWriter(
                    f, user_registry.commands, Command_Item)
                w.write()

        for context in all_commands.contexts:
            if context.commands.__len__() == 0:
                continue

            csv_file = csv_ctx_dir / f'{context.pretty_name}.csv'
            with open(csv_file, "w", newline='') as f:
                w = DataclassWriter(f, context.commands,
                                    Command_Item, delimiter='\t')
                w.write()

        # Latex File Generation
        for user_registry in all_commands.user_registry:
            table_file = latex_tables_dir_reg / \
                f'{user_registry.pretty_name}.kvt'
            table_file.write_text(user_registry.latex)

        for context in all_commands.contexts:
            if context.commands.__len__() == 0:
                continue

            table_file = latex_tables_dir_ctx / \
                f'{context.pretty_name}.kvt'
            table_file.write_text(context.latex)

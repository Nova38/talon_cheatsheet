




from talon import  Module, actions, registry
import sys, os, json

from talon.scripting import context

from user.knausj_talon.code.code import commands_updated


from dataclasses import asdict, dataclass, field


user_registry_list = ['user.letter','user.number_key','user.modifier_key',
                      'user.special_key','user.symbol_key','user.arrow_key',
                      'user.punctuation','user.function_key']




@dataclass(frozen=True)
class Context_Command():
    name: str
    command: str 
    # description: str
    os: str = ""
@dataclass
class Context_List:
    name: str
    pretty_name: str = ""
    os: str = ""
    # description: str
    raw_commands: list[dict] = field(default_factory=list)
    commands: list[Context_Command] = field(default_factory=list)
    
    def __post_init__(self):
        self.pretty_name,self.os = get_pretty_context_name(self.name)
        self.commands = [Context_Command(name=command.rule.rule, command=command.target.code,os=self.os)
                         for  command in registry.contexts[self.name].commands.values()
                        ]

@dataclass(frozen=True)
class Registry_Command:
    name: str
    command: str
@dataclass
class Registry_List:
    name: str
    pretty_name: str = ""
    registry: str = ""
    # os: str = ""
    commands: list[Registry_Command] = field(default_factory=list)

    def __post_init__(self):
        self.commands = [Registry_Command(name=name,command=command) for name,command in registry.lists[self.name][0].items()]
        self.registry = self.name.split(".")[0]
        self.pretty_name = self.name.split(".")[1]



@dataclass
class command_list:
    user_registry:  field(default_factory=list([Registry_Command]))
    contexts:       field(default_factory=list([Context_List]))


def get_pretty_context_name( name:str):
    ## The logic here is intended to only print from talon files that have actual voice commands.  
        splits = name.split(".")
        index = -1
        
        os_name = ""
        
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
    
        return (short_name,os_name)

mod = Module()



@mod.action_class
class user_actions:
    def json_cheatsheet():
        """Print out a sheet of talon commands"""
        
        all_commands = command_list(
            user_registry = [Registry_List(name = reg_name) for reg_name in user_registry_list],
            contexts = [Context_List(name=name) for name in registry.contexts]
        )

        this_dir = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.join(this_dir, 'cheatsheet.json')
        file = open(file_path,"w") 

        json_commands = json.dumps(asdict(all_commands), indent=4)
        file.write(json_commands)

        file.close()
        

import re

class ConfigFile:

    def __init__(self, filename):
        self.filename = 'config/{}'.format(filename)
        self.sections = []
        self.config = {}

    def read(self):
        configfile = open(self.filename)
        sectionre = re.compile('\[(.*)\]')
        entryre = re.compile('(.*)=(.*)')
        stringre = re.compile('"(.*)"')
        intre = re.compile('[0-9]*')
        commentre = re.compile('^#.*')
        
        for line in configfile:
            line = line.strip()
            if line == '' or line == ' ': continue
            if commentre.search(line): continue
            if sectionre.search(line):
                section = sectionre.search(line).group(1)
                if section not in self.sections: self.sections.append(section)
                self.config[section] = {}
                current_section = section
            elif entryre.search(line):
                entry = entryre.search(line)
                entry_val = entry.group(2)
                if stringre.search(entry_val):
                    entry_val = stringre.search(entry_val).group(1).strip()
                    if entry_val.startswith('!'):
                        entry_val = entry_val[1:].split(',')
                        entry_val = [a.strip() for a in entry_val]
                elif intre.search(entry_val):
                    entry_val = int(intre.search(entry_val.strip()).group(0))
                self.config[current_section][entry.group(1).strip()] = entry_val
        configfile.close()

    def reload(self):
        self.read()

    def write(self, config=None, filename=None):
        if config == None: config = self.config
        if filename == None: filename = self.filename
        filename = filename.split('.')
        configfile = open('{}_new.{}'.format(filename[0], filename[1]), 'w')
        for section, entry in config.items():
            configfile.write('[{}]'.format(section))
            for key, value in entry.items():
                if isinstance(value, str): value = '"{}"'.format(value)
                configfile.write('\n{}={}'.format(key, value))
            configfile.write('\n\n')
        configfile.close()
        import os
        os.remove('{}.{}'.format(filename[0], filename[1]))
        os.rename('{}_new.{}'.format(filename[0], filename[1]), '{}.{}'.format(filename[0], filename[1])) 

    def set_section(self, section):
        self.sections.append(section)
        self.config[section] = {}

    def set_entry(self, section, key, value):
        if section not in self.sections: self.set_section(section)
        self.config[section][key] = value

    def remove_section(self, section):
        self.sections.remove(section)
        self.config.pop(section)

    def remove_entry(self, section, key):
        self.config[section].pop(key)

    def __repr__(self):
        return 'Config File Object : {}'.format(self.filename)
    
    def __len__(self):
        return len(self.sections)

    def __getitem__(self, conf):
        if len(conf) == 2:
            section, entry = conf
            return self.config[section][entry]
        else:
            section = conf
            return self.config[section]

    def __setitem__(self, sec_key, entry_val):
        section, entry_key = sec_key
        if section not in self.sections: self.sections.append(section)
        if section not in self.config.keys(): self.config[section] = {}
        self.config[section][entry_key] = entry_val
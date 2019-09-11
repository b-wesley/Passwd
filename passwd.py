import re

std = re.compile(r'(?P<user>.*?):\*:(?P<uid>\d{1,11}):(?P<gid>\d{1,11}):(?P<gecos>.*?):/(?P<homeDir>.*?):/(?P<bin>.*?)\n')
noGecos = re.compile(r'(?P<user>.*?):\*:(?P<uid>\d{1,11}):(?P<gid>\d{1,11}):/(?P<homeDir>.*?):/(?P<bin>.*?)\n')
noHomeDir = re.compile(r'(?P<user>.*?):\*:(?P<uid>\d{1,11}):(?P<gid>\d{1,11}):(?P<gecos>.*?):/(?P<bin>.*?)\n')

regexList = [std, noGecos, noHomeDir]

class Account:
    def __init__(self, usrString):
        self.usrString = str(usrString)
        self.uidMatch = re.match(std, self.usrString)
        self.fields = {}
        
        self.tryMatch(regexList)
        self.setGivenFields()
        self.checkFields()

    #check if the account is correctly formatted
    def acctOk(self):
        return std.match(self.usrString)

    #check if there's a match for the user and a regex, if not try next regex in list
    def tryMatch(self, regexes):
        if regexes != []: #if the list is not empty, set the match
            self.uidMatch = regexes[0].match(self.usrString)
            if not self.uidMatch: #if there's not a match, try the next regex
                self.tryMatch(regexes[1:])
            else:
                self.fields = self.uidMatch.groupdict()

    #determine format of Gecos, initializes it accordingly
    def setGecos(self):
        try: 
            self.setField('gecos', self.uidMatch.group('gecos'))
        except:
            if self.acctOk():
                self.setField('gecos', ','.join([self.fields['gecos1'],
                                                 self.fields['gecos2'],
                                                 self.fields['gecos3']]))
                del self.fields['gecos1']
                del self.fields['gecos2']
                del self.fields['gecos3']
            else:
                self.setField('gecos', ' ')

    #set the given field to the given value            
    def setField(self, fieldName, newVal, update = False):
        self.fields[fieldName] = newVal 
        if update == True:
            self.updateUsrString()

    #update the usrString to match the fields
    def updateUsrString(self):
        self.usrString = ':'.join([self.fields['user'], self.fields['passwd'], self.fields['uid'], self.fields['gid'],
                                   self.fields['gecos'], self.fields['homeDir'], self.fields['bin']])

    #set fields based on match object
    def setGivenFields(self): 
        self.setField('user', self.uidMatch.group('user'))
        self.setField('passwd', '*')
        self.setField('uid', self.uidMatch.group('uid'))
        self.setField('gid', self.uidMatch.group('gid'))
        self.setField('bin', self.uidMatch.group('bin'))
        
        try: 
            self.setField('homeDir', self.uidMatch.group('homeDir'))
        except:
            self.setField('homeDir', '/home/' + self.fields['user'])
            
        self.fixDirs()
        self.setGecos()
        self.updateUsrString()
        
    #check if gecos and homeDir are defined, if not, adds them with empty value
    def checkFields(self):
        if 'homeDir' not in self.fields.keys():
            self.fields['homeDir'] = ' '
        if 'gecos' not in self.fields.keys():
            self.fields['gecos'] = ' '

    #check if homeDir and bin are in correct format, fixes them if not
    def fixDirs(self):
        if not self.fields['homeDir'].startswith("/"):
            self.fields['homeDir'] = '/' + self.fields['homeDir']
        if not self.fields['bin'].startswith("/"):
            self.fields['bin'] = '/' + self.fields['bin'] + '\n'


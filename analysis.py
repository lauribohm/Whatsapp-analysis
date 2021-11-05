import re
import regex
import pandas as pd
import emoji

def startsWithDateAndTime(s):
    pattern = '^\[\d{1,2}.\d{1,2}.\d{4}, \d{1,2}.\d{1,2}.\d{1,2} [AP]M\]'
    result = re.search(pattern, s)
    if result:
        return True
    return False
  
def FindAuthor(s):
    patterns = [
        '[\w]+:',                          
        '[\w]+[\s]+[\w]+:',                
        '([\w]+[\s]+[\w]+[\s]+[\w]+):',    
        '([\w]+)[\u263a-\U0001f999]+:',                
    ]
    pattern = '^' + '|'.join(patterns)
    result = re.search(pattern, s)
    if result:
        return True
    return False

def getDataPoint(line): 
    line = line[1:] 
    splitLine = line.split(']') 
    dateTime = splitLine[0]
    message = ' '.join(splitLine[1:])
    message = message[1:]
    message = message.replace('ä','a')  
    message = message.replace('ö','o')   
    message = message.replace('Ä','A')   
    message = message.replace('Ö','O')
    message = message.strip('\t')  
    if FindAuthor(message): 
        splitMessage = message.split(': ') 
        author = splitMessage[0] 
        message = ' '.join(splitMessage[1:])
    else:
        author = None
        message = message[1:]
    return dateTime, author, message

def transformDateTime(dateTime):
    dt = dateTime.split(',')
    date = dt[0]
    time = dt[1]
    date = date.split('.')
    date = date[2] + '-' + date[1] + '-' + date[0]
    time = time.replace('.', ':')
    dt = date + ' ' + time 
    return dt

parsedData = [] 

conversationPath = './data/_chat.txt' 
with open(conversationPath, encoding="utf-8") as fp:
    fp.readline() 
    messageBuffer = [] 
    datetime, author = None, None
    c = 0
    while True:
        line = fp.readline()
        c = c+1
        if ('image omitted' in line):
            line = line[1:]
        else:
            line = line.strip('\t')
        if not line: 
            break
        line = line.replace('ä','a')  
        line = line.replace('ö','o')   
        line = line.replace('Ä','A')   
        line = line.replace('Ö','O')
        line = line.strip() 
        if startsWithDateAndTime(line): 
            if len(messageBuffer) > 0: 
                parsedData.append([dateTime, author, ' '.join(messageBuffer)]) 
            messageBuffer.clear() 
            dateTime, author, message = getDataPoint(line)
            dateTime = transformDateTime(dateTime) 
            messageBuffer.append(message) 
        else:
            messageBuffer.append(line)
   
chat = pd.DataFrame(parsedData, columns=['DateTime', 'Author', 'Message']) 

chat["DateTime"] = pd.to_datetime(chat["DateTime"])

chat['weekday'] = chat['DateTime'].apply(lambda x: x.day_name())

chat['month_sent'] = chat['DateTime'].apply(lambda x: x.month_name()) 

chat['date'] = [d.date() for d in chat['DateTime']] 

chat['hour'] = [d.time().hour for d in chat['DateTime']]

URLPATTERN = r'(https://\S+)'
chat['urlcount'] = chat.Message.apply(lambda x: re.findall(URLPATTERN, x)).str.len()

chat['Letter_Count'] = chat['Message'].apply(lambda s : len(s))

chat['Word_Count'] = chat['Message'].apply(lambda s : len(s.split(' ')))

def get_emoji(text):
    emoji_list = []
    data = regex.findall(r'\X', text)
    #print(data)
    for char in data:
        c = (emoji.demojize(char))
        if (len(c) > 1):
            emoji_list.append(char)
    return emoji_list

chat["emoji"] = chat["Message"].apply(get_emoji)

def get_emoji_string(text):
    emoji_list = []
    data = regex.findall(r'\X', text)
    for char in data:
        c = (emoji.demojize(char))
        if (len(c) > 1):
            emoji_list.append(c)
    return emoji_list

chat.to_csv('results/_result.csv', encoding=('utf-8'))

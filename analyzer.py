import sys
import datetime
import calendar
import plotly


# month day year
current_date = [0, 0, 0]

user_list = list()

# key is users and values are tuples of message count and word count of user, tuple format is (msg count, word count)
user_count_dict = dict()
# key is users and values are a list of tuples of first texts sent by user, tuple format is (date, first text)
first_txt_dict = dict()

# these are the 'time dicts' referenced later in the program
chat_hour_dict = dict()
chat_month_dict = dict()
chat_day_dict = dict()

# stores a count of all websites shared by each user
shared_website_dict = dict()


# identify if message is a new one sent by a user rather than a newline continuation of a previous message
def identify_user_message(message):
    if '[' in message and ']' in message and message.count(':') >= 3:
        return True
    return False


# function to identify all users in chat
def identify_users(message):
    if identify_user_message(message):
        user = message.split(']')
        user = user[1].split(':')
        user = user[0] + ':'
        if user not in user_list:
            user_list.append(user)


# given a date, update time dicts
def update_time_dicts(date):
    month = date[0]
    day = date[1]
    year = date[2]
    hour = date[3]
    period = date[4]

    # if month present in dictionary, increment by one. else, set to 0 then add 1
    chat_month_dict[month] = chat_month_dict.get(month, 0) + 1

    # convert hour into 12AM str format, then increment if present
    hour = str(hour) + period
    chat_hour_dict[hour] = chat_hour_dict.get(hour, 0) + 1

    # convert month, day, year into a day of the week
    # first convert year to usable format XXXX rather than just 'XX
    year = '20' + year
    year = int(year)
    month = int(month)
    day = int(day)
    weekday = calendar.day_name[calendar.weekday(year, month, day)]
    chat_day_dict[weekday] = chat_day_dict.get(weekday, 0) + 1


# print out chat time patterns
def chat_time_patterns():
    # DEBUG should replace this block of code with function call to monthly pattern visual
    total = sum(chat_month_dict.values())
    top_month = None
    top_month_value = max(chat_month_dict.values())
    for keys, values in chat_month_dict.items():
        # returns str representation of month(given as int value)
        month = calendar.month_abbr[int(keys)]
        print(month + ': ' + str(round(values/total * 100)) + '%')
        if values == top_month_value:
            top_month = month
    print('Chatted the most on month:', top_month)

    print()

    total = sum(chat_hour_dict.values())
    top_hour = None
    top_hour_value = max(chat_hour_dict.values())
    for keys, values in chat_hour_dict.items():
        print(keys + ': ' + str(round(values / total * 100, 2)) + '%')
        if values == top_hour_value:
            top_hour = keys
    print('chatted the most at hour:', top_hour)

    print()

    total = sum(chat_day_dict.values())
    top_day = None
    top_day_value = max(chat_day_dict.values())
    for keys, values in chat_day_dict.items():
        print(keys + ': ' + str(round(values / total * 100)) + '%')
        if values == top_day_value:
            top_day = keys
    print('chatted the most on day:', top_day)


# prints list of who sent the first text on a given day, have to add first texts to dict? matching users
def first_txt_by_day(message):
    date = return_time_struct(message)
    if greater_current_date(date):  # if True then is first message of the day
        for user in user_list:
            if user in message:
                first_msg = message.split(user)
                user = user.split(':')[0]
                x = datetime.datetime(current_date[2], current_date[0], current_date[1])
                if user not in first_txt_dict:
                    first_txt_dict[user] = [(x.strftime('%b %d \'%Y'), first_msg[1])]
                else:
                    first_txt_dict[user].append((x.strftime('%b %d \'%Y'), first_msg[1]))


# counts number of messages and words sent by each user
# DEBUG function doesn't account for when multi-line messages are sent in one message
def num_words_messages(msg):
    for user in user_list:
        if user in msg:
            new_msg = msg.split(user)
            user = user.split(':')[0]
            if user not in user_count_dict:
                # set to 1 for message count and to the length of the message split by whitespace for word count
                user_count_dict[user] = [(1, len(new_msg[1].split()))]
            else:
                # add up previous values with new values and replace
                msg_count = user_count_dict[user][0][0] + 1
                word_count = user_count_dict[user][0][1] + len(new_msg[1].split())
                user_count_dict[user] = [(msg_count, word_count)]


# takes a line/message and returns a usable format of time
def return_time_struct(msg):
    # make list and then convert to tuple?
    stamp = msg[1:21]
    dstmp = stamp.split('/', 2)
    month = dstmp[0]
    day = dstmp[1]
    year = dstmp[2][0:2]
    stamp2 = dstmp[2][4:].split(':')
    hour = stamp2[0]
    minute = stamp2[1]
    second = stamp2[2][0:2]
    period = stamp2[2][3:5]
    # potential bug fix where full period not showing
    if 'A' in period:
        period = 'AM'
    else:
        period = 'PM'
    # fixed weird bug where brackets appear in month values - don't know why it occurs - didn't look into it that much
    if '[' in month:
        month = month.replace('[', '')
    time_struct = [month, day, year]
    # this struct only used for updating time structs in function below
    time_struct2 = [month, day, year, hour, period]
    update_time_dicts(time_struct2)
    return time_struct


# verifies if message is greater than current date
def greater_current_date(d):
    global current_date
    # map strs in list to ints
    d = list(map(int, d))
    # won't update correctly if year isn't taken into account as well
    if d > current_date or d[2] > current_date[2]:
        current_date = d
        return True
    else:
        return False


# keeps count of all websites shared
def store_shared_websites(message):
    if 'http://' in message or 'https://' in message:
        website = message.split('//')[1].split('/')[0]
        shared_website_dict[website] = shared_website_dict.get(website, 0) + 1


# prints which website is shared the most along with percentage of other websites
def shared_websites_patterns():
    total = sum(shared_website_dict.values())
    top_website = None
    top_website_value = max(shared_website_dict.values())
    for keys, values in shared_website_dict.items():
        print(keys + ': ' + str(round(values/total * 100)) + '%')
        if values == top_website_value:
            top_website = keys
    print('Most shared website:', top_website)


# # display bar graph visual of month chat patterns
# def display_month_chat_visual():
#     total = sum(chat_month_dict.values())
#     top_month = None
#     top_month_value = max(chat_month_dict.values())
#     x1 = []
#     y1 = []
#     percent_text = []
#     # fill list with values for month
#     for month_num in range(1, 13):
#         x1.append(calendar.month_abbr[month_num])
#
#     for num in range(0, 101, 10):
#         y1.append(num)
#
#     for key in sorted(chat_month_dict):
#         percentage = round(chat_month_dict[key]/total * 100)
#         percent_text.append(percentage)
#
#     trace0 = go.Bar(
#         x=x1,
#         y=y1,
#         text=percent_text,
#         marker=dict(
#             color='rgb(158,202,225)',
#             line=dict(
#                 color='rgb(8,48,107)',
#                 width=1.5,
#             )
#         ),
#         opacity=0.6
#     )
#
#     data = [trace0]
#     layout = go.Layout(
#         title='Monthly Chat Patterns',
#     )
#
#     fig = go.Figure(data=data, layout=layout)
#     py.iplot(fig, filename='text-hover-bar')
#
#     # for keys, values in chat_month_dict.items():
#     #     # returns str representation of month(given as int value)
#     #     month = calendar.month_abbr[int(keys)]
#     #     print(month + ': ' + str(round(values/total * 100)) + '%')
#     #     if values == top_month_value:
#     #         top_month = month
#     # print('Chatted the most on month:', top_month)


def main():
    chatfile = sys.argv[1]

    print('Opening chat file...')

    try:
        chatfilehand = open(chatfile, 'r', encoding='utf-8')
    except FileNotFoundError:
        print('ERROR:', chatfile, 'not found!')
    else:
        print('file opened successfully.')

    for line in chatfilehand:
        # print(line)
        identify_users(line)
        if identify_user_message(line):
            first_txt_by_day(line)
            store_shared_websites(line)
        num_words_messages(line)

    print('\nFirst texts: ')
    first_txt_total = 0
    # this loops will provide total # of values and also print all first texts
    for key, values in first_txt_dict.items():
        first_txt_total += len(first_txt_dict[key])
        for v in values:
            print(key, ":", v)

    print()

    # this loop provides percentage info of first texts sent by each user
    for key, values in first_txt_dict.items():
        user_total = len(first_txt_dict[key])
        print(key, 'sent', user_total, 'of the first texts, accounting for',
              round(user_total/first_txt_total * 100), '% of the first texts')

    print('\nUsers in chat: ')
    for item in user_list:
        print(item.split(':')[0])

    print('\nMessage count info: (number of messages, number of words)')
    for key, values in user_count_dict.items():
        for v in values:
            print(key, ':', v)

    print('\nchat time patterns: ')
    chat_time_patterns()

    print('\nshared website patterns: ')
    shared_websites_patterns()

    print('displaying monthly chat visual: ')
    # display_month_chat_visual()


if __name__ == '__main__':
    main()









import re
import pandas as pd

def preprocess(data):
    pattern = r'\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s(?:AM|PM)\s-\s(.*?)(?=\n\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s(?:AM|PM)\s-|$)'
    messages = re.findall(pattern, data, re.DOTALL)

    pattern = r'(\d{1,2}/\d{1,2}/\d{2,4}),\s(\d{1,2}):(\d{2})\s(AM|PM)'
    timestamps = re.findall(pattern, data)

    # Format timestamps in the desired output format
    dates = []
    for date, hour, minute, period in timestamps:
        hour_24hr = int(hour) + 12 if period == 'PM' else int(hour)
        dates.append(f"{date}, {hour_24hr:02d}:{minute} -")

        pattern = r'(\d{1,2}/\d{1,2}/\d{2,4}),\s(\d{1,2}):(\d{2})\s(AM|PM)'
        timestamps = re.findall(pattern, data)

        # Format timestamps in the desired output format
        formatted_timestamps = []
        for date, hour, minute, period in timestamps:
            hour_24hr = int(hour) + 12 if period == 'PM' and hour != '12' else int(hour)
            if hour_24hr == 24:
                date = pd.to_datetime(date, format='%m/%d/%y') + pd.DateOffset(days=1)
                hour_24hr = 0
            formatted_timestamps.append(f"{date}, {hour_24hr:02d}:{minute} -")

        # Create a DataFrame from messages and formatted timestamps
        df = pd.DataFrame({'user_message': messages, 'message_date': formatted_timestamps})

        # Convert message_date column to datetime
        df['message_date'] = pd.to_datetime(df['message_date'], format='%m/%d/%y, %H:%M -')

        df.rename(columns={'message_date': 'date'}, inplace=True)

        users = []
        messages = []
        for message in df['user_message']:
            entry = re.split('([\w\W]+?):\s', message)
            if entry[1:]:
                users.append(entry[1])
                messages.append(entry[2])
            else:
                users.append('group_notification')
                messages.append(entry[0])
        df['user'] = users
        df['message'] = messages
        df.drop(columns=['user_message'], inplace=True)

        df['only_date'] = df['date'].dt.date
        df['year'] = df['date'].dt.year
        df['month_num'] = df['date'].dt.month
        df['month'] = df['date'].dt.month_name()
        df['day'] = df['date'].dt.day
        df['day_name']=df['date'].dt.day_name()
        df['hour'] = df['date'].dt.hour
        df['minute'] = df['date'].dt.minute

        return df
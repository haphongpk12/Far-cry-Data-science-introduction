#!/usr/bin/env python3
from datetime import datetime
from datetime import timedelta, tzinfo, timezone
import csv, sqlite3


def read_log_file(log_file_pathname):
    """
    Waypoint 1: Read Game Session Log File
    @param: log_file_pathname -> representing the pathname of
            a Far Cry server log file, and reads
    @return: all the bytes from the file.
    """
    # Open file and read with rb mode
    input_file = open(log_file_pathname, "rb")
    # Store all content of file into log_data
    log_data = input_file.read()
    # Close file
    input_file.close()
    # Return log_data
    return log_data


def parse_log_start_time(log_data):
    """
    Waypoint 2: Parse Far Cry Engine's Start Time
        - We need to parse this date and time information to
        later determine the timestamp of each frag.
    @param: log_data -> representing the data read
            from a Far Cry server's log file
    @return: datetime.datetime object representing the time
            the Far Cry engine began to log events.
    Waypoint 3: Parse Far Cry Engine's Start Time with Time Zone
        - We generally define a time with its corresponding time zone
        related to UTC, also known as UTC offset.
        - Update this function parse_log_start_time to return
        a datetime.datetime object with time zone information.
    """
    # Split lines of content into a list
    log_data = log_data.decode("utf-8").splitlines()
    # Get Log started time
    str_time = " ".join(log_data[0].split()[4:])
    # Get time zone of location
    time_zone = get_time_zone(log_data)
    # Check error for time zone
    if int(time_zone) <= -24 or int(time_zone) >= 24:
        return "ValueError"
    else:
        # Convert normal time to datetime object
        log_start_time = datetime.strptime(str_time, "%B %d, %Y %H:%M:%S")
        # Insert timezone into tzinfo
        tzinfo = timezone(timedelta(hours=int(time_zone)))
        # Replace Log started time with time zone
        log_start_time = log_start_time.replace(tzinfo=tzinfo).isoformat()
        # Return log_start_time
        return log_start_time


def get_time_zone(log_data):
    """
    Get time zone in line where 'g_timezone' exists
    @param: log_data -> content of log file
    @return: time zone after take
    """
    for line in log_data:
        # Check if "g_timezone" exists
        if "g_timezone" in line:
            parse_line = line.split()
            # Strip trash element to get full time zone
            time_zone = parse_line[-1].split(",")[1].strip(")")
    # Return time zone
    return time_zone


def parse_session_mode_and_map(log_data):
    """
    Waypoint 4: Parse Match's Map Name and Game Mode
        - When you start a multiplayer session,
        you select which mode and map to play with.
        The Far Cry engine saves this information in its log file
    @param: log_data -> representing the data read from
            a Far Cry server's log file
    @return: tuple (mode, map)
    """
    # Split lines of content into a list
    log_data = log_data.decode("utf-8").splitlines()
    for line in log_data:
        # Check if "Loading level" exists
        if "Loading level" in line:
            # Split line into list to handle
            parse_line = line.split()
    for i in range(len(parse_line)):
        # Check if "Levels" in index of list
        if "Levels" in parse_line[i]:
            # map is element behind "/" with strip many trash things
            map = parse_line[i].split("/")[1].strip(",")
        if parse_line[i] == "mission":
            # mode is element behing "mission"
            mode = parse_line[i + 1]
    # Return tuple (mode, map)
    return (mode, map)


def parse_frags(log_data):
    """
    Waypoint 5: Parse Frag History
    @param: log_data -> representing the data read from
            a Far Cry server's log file
    @return: list of frags
        - Each frag is represented by a tuple in the following form:
            (frag_time, killer_name, victim_name, weapon_code)
        - Or, a simpler form, if the player committed suicide:
            (frag_time, killer_name)
        - Where:
            frag_time (required): Time when the frag occurred
                                  in the format MM:SS;
            killer_name (required): Username of the player
                                    who fragged another or killed himself;
            victim_name (optional): Username of the player
                                    who has been fragged;
            weapon_code (optional): Code name of the weapon
                                    that was used to frag.
    Waypoint 6: Include Time Zone To Frag Timestamps
        - Rewrite the function parse_frags so that the time of each frag
        returned is a datetime.datetime object with a time zone.
    """
    # Create empty list_of_frags
    list_of_frags = []
    # Get Log started time
    log_start_time = parse_log_start_time(log_data)
    # Split lines of content into a list
    log_data = log_data.decode("utf-8").splitlines()
    for line in log_data:
        if "killed" in line:
            # Check for suicide case of player
            if "itself" in line:
                # Return time and element of frags
                log_start_time, index, name, parse_line = return_time_and_element(line, log_start_time)
                list_of_frags.append((log_start_time, name))
            else:
                # Return time and element of frags
                log_start_time, index, name, parse_line = return_time_and_element(line, log_start_time)
                list_of_frags.append((
                                      log_start_time,
                                      name,
                                      parse_line[index + 1],
                                      parse_line[-1]))
    # Return list_of_frags
    return list_of_frags


def return_time_and_element(line, log_start_time):
    """
    This function will return time and element that
    one frags have to had
    """
    # Update hour when server reset time
    parse_line, log_start_time = update_hour(line, log_start_time)
    # Return index of string "killed" exists
    index = index_of_killed(parse_line)
    # Full name of player, it's in front of "killed"
    name = " ".join(parse_line[2:index])
    # Return time, index of killed, player name and list of line
    return log_start_time, index, name, parse_line


def index_of_killed(parse_line):
    """
    This function will find index of string "killed" exists
    """
    for i in range(len(parse_line)):
        if parse_line[i] == "killed":
            # Create variable index to store index of "killed"
            index = i
    # Return index
    return index


def update_hour(line, log_start_time):
    """
    This function will update hour when server reset time
    """
    parse_line = line.split()
    # Get run time of line
    tmp_time = parse_line[0].strip("><")
    # Compare minute of run time and last origin time
    if int(tmp_time.split(":")[0]) < int(log_start_time[14:16]):
        # If true, plus hour to one
        log_start_time = log_start_time.replace(log_start_time[11:13], str(int(log_start_time[11:13]) + 1))
    # Replace full time of one frag
    log_start_time = log_start_time.replace(log_start_time[14:19], tmp_time)
    # Return line and time
    return parse_line, log_start_time


def prettify_frags(frags):
    """
    Waypoint 7: Prettify Frag History
    @param: frags -> an array of tuples of frags parsed from
            a Far Cry server's log file
    @return: a list of strings, each with the following format:
            [frag_time] 😛 killer_name weapon_icon 😦 victim_name
            or, a simpler form, if the player committed suicide:
            [frag_time] 😦 victim_name ☠
    """
    list_of_strings = []
    # Create list of weapon code to convert into emoji
    gun_list = [
                "Falcon", "Shotgun", "P90", "MP5", "M4", "AG36", "OICW",
                "SniperRifle", "M249", "MG", "VehicleMountedAutoMG", "VehicleMountedMG"]
    bomp_list = ["AG36Grenade", "HandGrenade", "OICWGrenade", "StickyExplosive"]
    vehicle_list = ["Vehicle"]
    rocket_list = ["Rocket", "VehicleMountedRocketMG", "VehicleRocket"]
    knife_list = ["Machete"]
    boat_list = ["Boat"]
    for frag in frags:
        frag = list(frag)
        # Replace time isoformat to be normal time
        frag[0] = frag[0].replace(frag[0][10:11], " ")
        # Edit format of time
        frag[0] = "[" + frag[0] + "]"
        # Check if player suicide
        if len(frag) == 2:
            # Insert icon for player
            frag.insert(1, "\U0001F620")
            # Insert suicide icon
            frag.insert(3, "\U0001F480")
        # Check if players kill other players
        else:
            # Swap position of weapon code and victim name
            frag.insert(len(frag), frag.pop(2))
            # Insert killer icon
            frag.insert(1, "\U0001F61B")
            # Insert gun icon
            if frag[3] in gun_list:
                frag.pop(3)
                frag.insert(3, "\U0001F52B")
            # Insert bomp icon
            elif frag[3] in bomp_list:
                frag.pop(3)
                frag.insert(3, "\U0001F4A3")
            # Insert vehicle icon
            elif frag[3] in vehicle_list:
                frag.pop(3)
                frag.insert(3, "\U0001F699")
            # Insert rocket icon
            elif frag[3] in rocket_list:
                frag.pop(3)
                frag.insert(3, "\U0001F680")
            # Insert knife icon
            elif frag[3] in knife_list:
                frag.pop(3)
                frag.insert(3, "\U0001F52A")
            # Insert boat icon
            elif frag[3] in boat_list:
                frag.pop(3)
                frag.insert(3, "\U0001F6E5")
            # Insert victim icon
            frag.insert(4, "\U0001F620")
        # Check for suicide output mode
        if len(frag) == 4:
            one_frag = frag[0] + " " + frag[1] + "  " + frag[2] + " " + frag[3]
        # Check for killer output mode
        else:
            one_frag = frag[0] + " " + frag[1] + "  " + frag[2] + " " + frag[3] \
                       + "  " + frag[4] + "  " + frag[5]
        # Append beautify frag into list
        list_of_strings.append(one_frag)
    # Return list
    return list_of_strings


def parse_game_session_start_and_end_times(log_data, log_start_time):
    """
    Waypoint 8: Determine Game Session's Start and End Times
    @param: log_data -> representing the data read from
            a Far Cry server's log file
            log_start_time -> get time to convert
    """
    log_data = log_data = log_data.decode("utf-8").splitlines()
    for line in log_data:
        # First time in fully loaded in is start_time
        if "loaded in" in line:
            start_time = line.split()[0].strip("><")
            break
    for line in log_data:
        # If "_ERRORMESSAGE" exists, return end_time
        if "_ERRORMESSAGE" in line:
            end_time = line.split()[0].strip("><")
            break
        # Elif "Statistics" exists, return end_time
        elif "Statistics" in line:
            end_time = line.split()[0].strip("><")
            break
    # Replace Log started time to be start_time
    start_time = log_start_time.replace(log_start_time[14:19], start_time)
    # Replace start_time to be normal time
    start_time = start_time.replace(start_time[10:11], " ")
    # Replace Log started time to be end_time
    end_time = log_start_time.replace(log_start_time[14:19], end_time)
    # Replace end_time to be normal time
    end_time = end_time.replace(end_time[10:11], " ")
    return start_time, end_time


def write_frag_csv_file(log_file_pathname, frags):
    """
    Waypoint 9: Create Frag History CSV File
        - To import our frag history data into a spreadsheet application,
        we need to store this data in a CSV file.
    @param: log_file_pathname -> representing the pathname of
            the CSV file to store the frags in
            frags -> list of frags in line by line
    """
    # Open file as csv file
    with open(log_file_pathname, "w", newline='') as csv_file:
        # Write content of file into csv file
        spam_writer = csv.writer(csv_file, quotechar=',')
        for frag in frags:
            frag = list(frag)
            frag[0] = frag[0].replace(frag[0][10:11], " ")
            # Write line by line into csv file
            spam_writer.writerow(frag)
    # Close csv file
    csv_file.close()



def insert_match_to_sqlite(file_pathname, start_time, end_time, game_mode, map_name, frags):
    """
    Waypoint 25: Insert Game Session Data into SQLite
        - The function insert_match_to_sqlite inserts a new record into the table match with the arguments
        start_time, end_time, game_mode, and map_name, using an INSERT statement
    """
    # Connect into database
    conn = sqlite3.connect(file_pathname)
    # Use cursor to execute query
    cursor = conn.cursor()
    # Insert query
    query = "INSERT INTO match(start_time,end_time,game_mode,map_name)" \
            "VALUES(?,?,?,?)"
    args = (start_time, end_time, game_mode, map_name)
    # Execute query
    cursor.execute(query, args)
    # Get id of field
    match_id = cursor.lastrowid
    # Close cursor
    cursor.close()
    # Commit connection
    conn.commit()
    # Insert frags
    insert_frags_to_sqlite(conn, match_id, frags)
    conn.close()


def insert_frags_to_sqlite(conn, match_id, frags):
    """
    Waypoint 26: Insert Match Frags into SQLite
    - The function insert_frags_to_sqlite
    inserts new records into the table match_frag.
    - Integrate this function in the function insert_match_to_sqlite.
    """
    # Use cursor to execute query
    cursor = conn.cursor()
    # Query for killer
    query1 = "INSERT INTO match_frag(match_id, frag_time,killer_name,victim_name,weapon_code)" \
            "VALUES(?,?,?,?,?)"
    # Query for suicider
    query2 = "INSERT INTO match_frag(match_id, frag_time,killer_name)" \
            "VALUES(?,?,?)"
    # Insert id into tuple of frag
    for i in range(len(frags)):
        frags[i] = list(frags[i])
        frags[i][0] = frags[i][0].replace(frags[i][0][10:11], " ")
        frags[i] = tuple(frags[i])
        frags[i] = (match_id,) + frags[i]
    for frag in frags:
        # Check for suicider
        if len(frag) == 3:
            cursor.execute(query2, frag)
        # Check for killer
        else:
            cursor.execute(query1, frag)
    # Commit connection
    conn.commit()
    cursor.close()


def main():
    """
    Main function: Use to run sub_function of program
    """
    log_data = read_log_file("./logs/log01.txt")
    log_start_time = parse_log_start_time(log_data)
    game_mode, map_name = parse_session_mode_and_map(log_data)
    frags = parse_frags(log_data)
    prettified_frags = prettify_frags(frags)
    write_frag_csv_file('./logs/log01.csv', frags)
    start_time, end_time = parse_game_session_start_and_end_times(log_data, log_start_time)
    insert_match_to_sqlite('./farcry.db', start_time, end_time, game_mode, map_name, frags)


if __name__ == "__main__":
    main()

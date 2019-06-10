"""
Waypoint 27: Select Start and End Times of Matches
"""
SELECT match_id, start_time, end_time
FROM match

"""
Waypoint 28: Select Game Mode and Map Name of Matches
"""
SELECT match_id, game_mode, map_name
FROM match

"""
Waypoint 29: Select all Columns of Matches
"""
SELECT *
FROM match

"""
Waypoint 30: Select distinct Killer Names
"""
SELECT DISTINCT killer_name
FROM match_frag

"""
Waypoint 31: Order the List of Killer Names
"""
SELECT DISTINCT killer_name
FROM match_frag
ORDER BY killer_name

"""
Waypoint 32: Calculate the Number of Matches
"""
SELECT COUNT(*)
FROM match

"""
Waypoint 33: Calculate the number of Kills and Suicides
"""
SELECT COUNT(*) AS kill_suicide_count
FROM match_frag

"""
Waypoint 34: Calculate the Number of Suicides
"""
SELECT (COUNT(*) - COUNT(victim_name)) AS suicide_count
FROM match_frag

"""
Waypoint 35: Calculate the Number of Kills (1)
"""
SELECT COUNT(kill_name) AS kill_count
FROM match_frag
WHERE victim_name IS NOT NULL

"""
Waypoint 36: Calculate the Number of Kills (2)
"""
SELECT COUNT(victim_name) AS kill_count
FROM match_frag

"""
Waypoint 37: Calculate the Number of Kills and Suicides per Match
"""
SELECT match_id, COUNT(*) AS kill_suicide_count
FROM match_frag
GROUP BY match_id

"""
Waypoint 38: Calculate and Order the Number of Kills and Suicides per Match
"""
SELECT match_id, COUNT(*) AS kill_suicide_count
FROM match_frag
GROUP BY match_id
ORDER BY kill_suicide_count DESC

"""
Waypoint 39: Calculate and Order the Number of Suicides per Match
"""
SELECT match_id, (COUNT(*) - COUNT(victim_name)) AS suicide_count
FROM match_frag
GROUP BY match_id

"""
Waypoint 40: Calculate and Order the Total Number of Kills per Player
"""
SELECT killer_name AS player_name, COUNT(killer_name) AS kill_count
FROM match_frag
GROUP BY killer_name

"""
Waypoint 41: Calculate and Order the Number of Kills per Player and per Match
"""
SELECT match_id, killer_name AS player_name, COUNT(killer_name) AS kill_count
FROM match_frag
GROUP BY match_id, killer_name
ORDER BY match_id ASC, kill_count DESC

"""
Waypoint 42: Calculate and Order the Number of Deaths per Player and per Match
"""
SELECT match_id, victim_name AS player_name, COUNT(victim_name) AS death_count
FROM match_frag
WHERE victim_name IS NOT NULL
GROUP BY match_id, victim_name
ORDER BY match_id ASC, death_count DESC

"""
Waypoint 43: Select Matches and Calculate the Number of Players and the Number of Kills and Suicides
"""
SELECT M.match_id, M.start_time, M.end_time, COUNT(DISTINCT killer_name) AS player_count, COUNT(*) AS kill_suicide_count
FROM match AS M, match_frag AS MF
WHERE M.match_id = MF.match_id
GROUP BY M.match_id
ORDER BY M.start_time ASC

"""This part of the scorecard provides all API calls for the frontend."""
from flask import Blueprint, render_template
import json
from random import randint, choice

app = Blueprint("api", __name__)


def get_all_group_user_ids(group_database):
    """
    Get all user IDs registered in groups.

    Args:
        group_database: The groups.db dictionary.

    Returns:
        A list of user ID strings.
    """
    return [
        user_id
        for group in group_database
        for user_id in group
        if isinstance(user_id, str)
    ]


@app.route("/make_id_for/<username>")
def make_id(username):
    """
    Create an ID for a user.

    Args:
        username: Username for the user.

    Returns:
        Where to redirect to with the ID.
    """
    print("Making ID for", username)
    try:
        id_database = json.load(open("ids.db"))
    except FileNotFoundError:
        id_database = {}
    new_id = str(randint(0, 999)).zfill(3)
    if username in id_database:
        old_id = id_database[username]
        try:
            group_database = json.load(open("groups.db"))
        except FileNotFoundError:
            group_database = []
        for group_index, group in enumerate(group_database):
            group[1:] = [user_id.replace(old_id, new_id) for user_id in group[1:]]
            group_database[group_index] = group
        print("Updating groups, now groups.db is", group_database)
        json.dump(group_database, open("groups.db", "w"))
    # First ID
    id_database[username] = new_id
    print("Updating IDs, now ids.db is", id_database)
    json.dump(id_database, open("ids.db", "w"))
    return f"/cluecard/{id_database[username]}"


@app.route("/add_ids/<existing_id>/<new_id>")
def add_ids(existing_id, new_id):
    """
    Group mechanic: Add two IDs together.

    Args:
        existing_id: The ID that's sending the add request.
        new_id: The ID to be added on.

    Returns:
        Whether it worked, and if it worked, what happened in order to merge.
    """
    existing_id = existing_id.zfill(3)
    new_id = new_id.zfill(3)
    try:
        all_ids = json.load(open("ids.db")).values()
    except Exception:
        all_ids = []
    if existing_id not in all_ids or new_id not in all_ids:
        try:
            json.load(open("ids.db"))
        except Exception:
            json.dump({}, open("ids.db", "w"))
        print(f"{existing_id} or {new_id} are not in {all_ids}")
        print(f'existing_id {"is" if existing_id in all_ids else "is not"} in ids')
        print(f'new_id {"is" if new_id in all_ids else "is not"} in ids')
        return "invalid_id"
    try:
        group_database = json.load(open("groups.db"))
    except FileNotFoundError:
        group_database = []
    all_group_ids = get_all_group_user_ids(group_database)
    for group in group_database:
        if existing_id in group and new_id in group:
            return "already_in_same_group"
    if existing_id in all_group_ids and new_id in all_group_ids:
        new_group = []
        for group in group_database:
            if new_id in group:
                new_group = group
        for group_index, group in enumerate(group_database):
            if existing_id in group:
                group_database[group_index] = group + new_group[1:]
                group_database.remove(new_group)
                print(group_database)
                json.dump(group_database, open("groups.db", "w"))
                return "merge_groups"
    elif existing_id in all_group_ids or new_id in all_group_ids:
        for group_index, group in enumerate(group_database):
            if existing_id in group or new_id in group:
                id_to_add = new_id if existing_id in group else existing_id
                group_database[group_index].append(id_to_add)
                print(group_database)
                json.dump(group_database, open("groups.db", "w"))
                return "add_to_group"
    else:
        # The best make you win, most tell you what it's not,
        # and some don't give you anything.
        clue_statuses = {}
        for clue_letter in "ABCD":
            for clue_number in range(1, 5):
                clue_statuses[clue_letter + str(clue_number)] = "regular"
        the_chosen_one = choice(["A", "B", "C", "D"]) + str(randint(1, 4))
        clue_statuses[the_chosen_one] = "correct"
        group_database.append([clue_statuses, existing_id, new_id])
        print(group_database)
        json.dump(group_database, open("groups.db", "w"))
        return "makenew"


@app.route("/user_status/<user_id>")
def user_status(user_id):
    """
    Find the current user status.

    Args:
        user_id: The user ID.

    Returns:
        A JSON string. Status can be bad_id, not_in_group, or success.
        If successful, then result is set to a list of people in the group.
        Example of success:
        {"status": "success", "result": ["Kendell", "Wendell"]}
    """
    try:
        id_database = json.load(open("ids.db"))
    except FileNotFoundError:
        id_database = {}
    if user_id not in id_database.values():
        return json.dumps({"status": "bad_id"})
    try:
        group_database = json.load(open("groups.db"))
    except FileNotFoundError:
        group_database = []
    try:
        metadata_database = json.load(open("metadata.db"))
    except FileNotFoundError:
        metadata_database = {}
    all_group_ids = get_all_group_user_ids(group_database)
    if user_id not in all_group_ids:
        return json.dumps({"status": "not_in_group"})
    for group in group_database:
        if user_id in group:
            try:
                id_database = json.load(open("ids.db"))
            except FileNotFoundError:
                id_database = {}
            group = group[1 : len(group)]
            inv_map = {user_id: name for name, user_id in id_database.items()}
            mgroup = [
                inv_map[person] + metadata_database.get(person, "")
                for person in group.copy()
            ]
            return json.dumps({"status": "success", "result": mgroup})


@app.route("/clue_status_of/<clue_id>/for/<user_id>")
def clue_status(clue_id, user_id):
    """
    Check a clue number for a user ID.

    Args:
        user_id: The user ID.
        clue_id: The clue ID.

    Returns:
        regular if the clue should give them a hint on what not to go to.
        correct if it means that they won.
    """
    try:
        group_database = json.load(open("groups.db"))
    except FileNotFoundError:
        group_database = []
    all_group_ids = get_all_group_user_ids(group_database)
    if user_id not in all_group_ids:
        return "not_in_group"
    for group in group_database:
        if user_id in group:
            if clue_id in group[0]:
                return group[0][clue_id]
            return "invalid_clue"


@app.route("/incorrect_clue_for/<user_id>/without/<excludes>")
def find_incorrect_clue(user_id, excludes):
    """
    Find an incorrect clue based on a user ID.

    Args:
        user_id: The user ID.
        excludes: A clue to not return.

    Returns:
        An incorrect clue for that ID that isn't excludes.
    """
    try:
        group_database = json.load(open("groups.db"))
    except FileNotFoundError:
        group_database = []
    all_group_ids = get_all_group_user_ids(group_database)
    if user_id not in all_group_ids:
        return "Not in a group"
    for group in group_database:
        if user_id in group:
            clues = []
            for clue_letter in "ABCD":
                for clue_number in range(1, 5):
                    clues.append(f"{clue_letter}{clue_number}")
            clue_to_return = ""
            while True:
                clue_to_return = choice(clues)
                if group[0][clue_to_return] != "correct" and clue_to_return != excludes:
                    break
            return clue_to_return


@app.route("/add_to_finished/<user_id>")
def add_to_finished(user_id):
    """
    Add a user ID to the finished database.

    Args:
        user_id: The user ID to be added.

    Returns:
        "done" and the current database.
    """
    try:
        metadata_database = json.load(open("metadata.db"))
    except FileNotFoundError:
        metadata_database = {}
    if user_id not in metadata_database:
        metadata_database[user_id] = " (🏁 finished)"
    json.dump(metadata_database, open("metadata.db", "w"))
    return f"done {metadata_database}"


@app.route("/debug/")
def debug():
    """
    List all databases.

    Returns:
        All of the databases.
    """
    try:
        group_database = json.load(open("groups.db"))
    except FileNotFoundError:
        group_database = []
    all_group_ids = get_all_group_user_ids(group_database)
    try:
        metadata_database = json.load(open("metadata.db"))
    except FileNotFoundError:
        metadata_database = {}
    try:
        id_database = json.load(open("ids.db"))
    except FileNotFoundError:
        id_database = {}
    return render_template(
        "debug.html",
        group_database=group_database,
        all_group_ids=all_group_ids,
        metadata_database=metadata_database,
        id_database=id_database,
    )

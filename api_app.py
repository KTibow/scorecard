"""This part of the scorecard provides all API calls for the frontend."""
from flask import Blueprint, render_template
import json
from random import randint, choice

app = Blueprint("api", __name__)


def get_all_user_ids(group_database):
    return [user_id for group in g for user_id in group if isinstance(user_id, str)]


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
    new_id = str(randint(0, 99999)).zfill(5)
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


@app.route("/add_ids/<exist>/<new>")
def add_ids(exist, new):
    """
    Group mechanic: Add two IDs together.

    Args:
        exist: The ID that's sending the add request.
        new: The ID to be added on.

    Returns:
        Whether it worked, and if it worked, what happened in order to merge.
    """
    exist = exist.zfill(5)
    new = new.zfill(5)
    try:
        aids = list(json.load(open("ids.db")).values())
    except Exception:
        aids = []
    if exist not in aids or new not in aids:
        try:
            json.load(open("ids.db"))
        except Exception:
            json.dump({}, open("ids.db", "w"))
        print(f"{exist} or {new} are not in {aids}")
        print(f'exist {"is" if exist in aids else "is not"} in ids')
        print(f'new {"is" if new in aids else "is not"} in ids')
        return "notreal"
    try:
        group_database = json.load(open("groups.db"))
    except FileNotFoundError:
        group_database = []
    comp = get_all_user_ids(group_database)
    for group in group_database:
        if exist in group and new in group:
            return "already"
    if exist in comp and new in comp:
        newgp = []
        for group in group_database:
            if new in group:
                newgp = group
        for group in group_database:
            if exist in group:
                group_database[group_database.index(group)] = (
                    group + newgp[1 : len(newgp)]
                )
                group_database.remove(newgp)
                print(group_database)
                json.dump(group_database, open("groups.db", "w"))
                return "merge"
    elif exist in comp and new not in comp:
        for group in group_database:
            if exist in group:
                group_database[group_database.index(group)].append(new)
                print(group_database)
                json.dump(group_database, open("groups.db", "w"))
                return "addnew"
    elif exist not in comp and new in comp:
        for group in group_database:
            if new in group:
                group_database[group_database.index(group)].append(exist)
                print(group_database)
                json.dump(group_database, open("groups.db", "w"))
                return "addexist"
    else:
        # The best make you win, most tell you what it's not,
        # and some don't give you anything.
        infodict = {}
        for clue_letter in "ABCD":
            for clue_number in range(1, 5):
                infodict[clue_letter + str(clue_number)] = "regular"
        the_chosen_one = choice(["A", "B", "C", "D"]) + str(randint(1, 4))
        infodict[the_chosen_one] = "correct"
        group_database.append([infodict, exist, new])
        print(group_database)
        json.dump(group_database, open("groups.db", "w"))
        return "makenew"


@app.route("/user_status/<uid>")
def user_status(uid):
    """
    Find the current user status.

    Args:
        uid: The user ID.

    Returns:
        A JSON string. Status can be bad_id, not_in_group, or success.
        If successful, then result is set to a list of people in the group.
    """
    try:
        id_database = json.load(open("ids.db"))
    except FileNotFoundError:
        id_database = {}
    if uid not in list(id_database.values()):
        return json.dumps({"status": "bad_id"})
    try:
        group_database = json.load(open("groups.db"))
    except FileNotFoundError:
        group_database = []
    try:
        metadata_database = json.load(open("metadata.db"))
    except FileNotFoundError:
        metadata_database = {}
    comp = get_all_user_ids(group_database)
    if uid not in comp:
        return json.dumps({"status": "not_in_group"})
    for group in group_database:
        if uid in group:
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


@app.route("/clue_status_of/<clue_id>/for/<uid>")
def clue_status(clue_id, uid):
    """
    Check a clue number for a user ID.

    Args:
        uid: The user ID.
        clue_id: The clue ID.

    Returns:
        regular if the card should give them a hint on what not to go to.
        correct if it means that they won.
    """
    try:
        group_database = json.load(open("groups.db"))
    except FileNotFoundError:
        group_database = []
    comp = get_all_user_ids(group_database)
    if uid not in comp:
        return "not_in_group"
    for group in group_database:
        if uid in group:
            if clue_id in group[0]:
                return group[0][clue_id]
            return "invalid_card"


@app.route("/incorrect_card_for/<uid>/without/<excludes>")
def find_incorrect_card(uid, excludes):
    """
    Find an incorrect card based on a user ID.

    Args:
        uid: The user ID.
        excludes: A card to not return.

    Returns:
        An incorrect clue for that ID that isn't excludes.
    """
    try:
        group_database = json.load(open("groups.db"))
    except FileNotFoundError:
        group_database = []
    comp = get_all_user_ids(group_database)
    if uid not in comp:
        return "-1"
    for group in group_database:
        if uid in group:
            clues = []
            for clue_letter in "ABCD":
                for clue_number in range(1, 5):
                    clues.append(clue_letter + str(clue_number))
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
    comp = get_all_user_ids(group_database)
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
        comp=comp,
        metadata_database=metadata_database,
        id_database=id_database,
    )

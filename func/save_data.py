from func.database import db, cursor

async def save_user_data(user_id, username):
    cursor.execute('''
    INSERT INTO users (username, discord_id)
    VALUES (%s, %s)
    ''', (username, user_id, ))
    db.commit()
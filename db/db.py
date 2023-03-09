import asyncpg
import asyncio
import configparser  
import os

config = configparser.ConfigParser()
config.read("config.ini")

user = config['DATABASE']['user']
password = config['DATABASE']['password']
host = config['DATABASE']['host']
port = config['DATABASE']['port']
database = config['DATABASE']['database']

#-----------------------------------------------------------------------------------------------------------------------------------

class ClientBotDB():
    async def nickname_exist(usr_id):
        connection = await asyncpg.connect(
            user=user,
            password=password,
            host=host,
            port=port,
            database=database
        )

        res = await connection.fetch(f"SELECT nickname FROM nickname_id WHERE usr_id = '{usr_id}'")
        return res

    async def add_nickname(usr_id, nickname, username):
        connection = await asyncpg.connect(
            user=user,
            password=password,
            host=host,
            port=port,
            database=database
        )

        async with connection.transaction():
            await connection.execute(f"INSERT INTO nickname_id (usr_id, nickname, username) VALUES ('{usr_id}', '{nickname}', '@{username}'); Commit;")


    async def add_to_db(pic_url, tag, description, usr_id, price, pic_name) -> None:
        connection = await asyncpg.connect(
            user=user,
            password=password,
            host=host,
            port=port,
            database=database
        )

        async with connection.transaction():
            await connection.execute(
                f'INSERT INTO pictures (pic_url, tag, description, usr_id, price, pic_name)' +
                f" VALUES ('{pic_url}', '{tag}', '{description}', '{usr_id}', CAST('{price}' AS BIGINT), '{pic_name}'); Commit;"
            )
        

    async def get_profile(usr_id):
        connection = await asyncpg.connect(
            user=user,
            password=password,
            host=host,
            port=port,
            database=database
        )

        async with connection.transaction():
            res = await connection.fetch(
                f"SELECT p.pic_url, p.number, p.tag, p.description, p.pic_name, n.nickname, p.price " +
                f"FROM pictures p " +
                f"INNER JOIN nickname_id n ON p.usr_id = n.usr_id " + 
                f"WHERE p.usr_id='{usr_id}' AND p.accept = true ORDER BY p.number;"
            )
        return res


    async def sale(usr_id, number):
        connection = await asyncpg.connect(
            user=user,
            password=password,
            host=host,
            port=port,
            database=database
        )

        async with connection.transaction():
            res = await connection.fetch(f"SELECT pic_url FROM pictures WHERE usr_id='{usr_id}'AND number={number};")
            if res:
                await connection.execute(f"UPDATE pictures SET sold=true WHERE usr_id='{usr_id}'AND number={number}; Commit;")
                return True
            else:
                return False

    async def del_pic(usr_id, number):
        connection = await asyncpg.connect(
            user=user,
            password=password,
            host=host,
            port=port,
            database=database
        )
    
        async with connection.transaction():
            res = await connection.fetch(f"SELECT pic_url FROM pictures WHERE usr_id='{usr_id}'AND number={number};")
            if res:
                os.remove(res[0][0])
                await connection.execute(f"DELETE FROM pictures WHERE usr_id='{usr_id}'AND number={number}; Commit;")
                await connection.execute(f"UPDATE pictures SET number=number-1 WHERE usr_id='{usr_id}'AND number>{number}; Commit;")
                await connection.execute(f"UPDATE nickname_id SET count_pics=count_pics-1 WHERE usr_id='{usr_id}'; Commit;")
                return True

            else:
                return False

#---------------------------------------------------------------------------------------------------------------------------------------------

class CatalogBotDB():
    async def get_pic_fromDB(sold=None, price=None, tag=None, pic_name=None, artist=None, usr_id=None):
        connection = await asyncpg.connect(
            user=user,
            password=password,
            host=host,
            port=port,
            database=database
        )

        if sold==None:
            sold = "NULL"
        else:
            sold = "false" 

        if tag==None:
            tag = "NULL"
        else:
            tag = f"'{tag}'"

        if pic_name==None:
            pic_name_check = "NULL"
            pic_name = ['1']
        else:
            pic_name_check = " NOT NULL"

        if artist==None:
            artist_check = "NULL"
            artist = ['1']
        else:
            artist_check = " NOT NULL"

        async with connection.transaction():
            if usr_id:
                res = await connection.fetch(
                    f"SELECT p.pic_url, p.pic_name, p.description, n.nickname, p.price, n.username, p.tag, p.usr_id  " +
                    f"FROM pictures p " + 
                    f"INNER JOIN nickname_id n ON p.usr_id = n.usr_id " + 
                    f"WHERE p.usr_id='{usr_id}' AND p.accept=true ORDER BY random() LIMIT 15; "
                )
            elif price==None:
                res = await connection.fetch(
                    f"SELECT p.pic_url, p.pic_name, p.description, n.nickname, p.price, n.username, p.tag, p.usr_id  " +
                    f"FROM pictures p " + 
                    f"INNER JOIN nickname_id n ON p.usr_id = n.usr_id " + 
                    f"WHERE CASE WHEN {tag} IS NOT NULL THEN p.tag= {tag} ELSE p.tag IS NOT NULL END " + 
                    f" AND CASE WHEN {sold} IS NOT NULL THEN p.sold={sold} ELSE p.sold IS NOT NULL END " +
                    f" AND CASE WHEN {pic_name_check} IS NOT NULL THEN LOWER(p.pic_name) LIKE ANY(ARRAY{pic_name}) ELSE p.pic_name IS NOT NULL END "
                    f" AND CASE WHEN {artist_check} IS NOT NULL THEN LOWER(n.nickname) LIKE ANY(ARRAY{artist}) ELSE n.nickname IS NOT NULL END "
                    f" AND p.accept = true ORDER BY random() LIMIT 15;"
                )
            elif price[1]=='':
                res = await connection.fetch(
                    f"SELECT p.pic_url, p.pic_name, p.description, n.nickname, p.price, n.username, p.tag, p.usr_id  " +
                    f"FROM pictures p " + 
                    f"INNER JOIN nickname_id n ON p.usr_id = n.usr_id " + 
                    f"WHERE CASE WHEN {tag} IS NOT NULL THEN p.tag= {tag} ELSE p.tag IS NOT NULL END " + 
                    f" AND CASE WHEN {sold} IS NOT NULL THEN p.sold={sold} ELSE p.sold IS NOT NULL END " +
                    f" AND CASE WHEN {pic_name_check} IS NOT NULL THEN LOWER(p.pic_name) LIKE ANY(ARRAY{pic_name}) ELSE p.pic_name IS NOT NULL END "
                    f" AND CASE WHEN {artist_check} IS NOT NULL THEN LOWER(n.nickname) LIKE ANY(ARRAY{artist}) ELSE n.nickname IS NOT NULL END "
                    f" AND p.price >= CAST({price[0]} AS BIGINT) " +
                    f" AND p.accept = true ORDER BY random() LIMIT 15;"
                )
            elif price[0]=='':
                res = await connection.fetch(
                    f"SELECT p.pic_url, p.pic_name, p.description, n.nickname, p.price, n.username, p.tag, p.usr_id  " +
                    f"FROM pictures p " + 
                    f"INNER JOIN nickname_id n ON p.usr_id = n.usr_id " + 
                    f"WHERE CASE WHEN {tag} IS NOT NULL THEN p.tag= {tag} ELSE p.tag IS NOT NULL END " + 
                    f" AND CASE WHEN {sold} IS NOT NULL THEN p.sold={sold} ELSE p.sold IS NOT NULL END " +
                    f" AND CASE WHEN {pic_name_check} IS NOT NULL THEN LOWER(p.pic_name) LIKE ANY(ARRAY{pic_name}) ELSE p.pic_name IS NOT NULL END "
                    f" AND CASE WHEN {artist_check} IS NOT NULL THEN LOWER(n.nickname) LIKE ANY(ARRAY{artist}) ELSE n.nickname IS NOT NULL END "
                    f" AND p.price <= CAST({price[1]} AS BIGINT) " +
                    f" AND p.accept = true ORDER BY random() LIMIT 15;"
                )
            else:
                res = await connection.fetch(
                    f"SELECT p.pic_url, p.pic_name, p.description, n.nickname, p.price, n.username, p.tag, p.usr_id  " +
                    f"FROM pictures p " + 
                    f"INNER JOIN nickname_id n ON p.usr_id = n.usr_id " + 
                    f"WHERE CASE WHEN {tag} IS NOT NULL THEN p.tag= {tag} ELSE p.tag IS NOT NULL END " + 
                    f" AND CASE WHEN {sold} IS NOT NULL THEN p.sold={sold} ELSE p.sold IS NOT NULL END " +
                    f" AND CASE WHEN {pic_name_check} IS NOT NULL THEN LOWER(p.pic_name) LIKE ANY(ARRAY{pic_name}) ELSE p.pic_name IS NOT NULL END "
                    f" AND CASE WHEN {artist_check} IS NOT NULL THEN LOWER(n.nickname) LIKE ANY(ARRAY{artist}) ELSE n.nickname IS NOT NULL END "
                    f" AND p.price >= CAST({price[0]} AS BIGINT) AND p.price <= CAST({price[1]} AS BIGINT)" +
                    f" AND p.accept = true ORDER BY random() LIMIT 15;"
                )
            return res


#---------------------------------------------------------------------------------------------------------------------------------------------

class AdminBotDB():
    async def get_pic():
        connection = await asyncpg.connect(
            user=user,
            password=password,
            host=host,
            port=port,
            database=database
        )

        async with connection.transaction():
            res = await connection.fetch(
                f"SELECT p.pic_url, p.tag, p.description, p.pic_name, p.usr_id, p.price, n.nickname " +
                f"FROM pictures p JOIN nickname_id n ON p.usr_id=n.usr_id WHERE accept=false LIMIT 1;"
            )
        return res


    async def del_pic(pic_url):
        connection = await asyncpg.connect(
            user=user,
            password=password,
            host=host,
            port=port,
            database=database
        )

        await connection.execute(f"DELETE FROM pictures WHERE pic_url='{pic_url}'; Commit;")
        os.remove(pic_url)


    async def add_pic(pic_url, usr_id):
        connection = await asyncpg.connect(
            user=user,
            password=password,
            host=host,
            port=port,
            database=database
        )

        number = await connection.fetch(f"SELECT count_pics FROM nickname_id WHERE usr_id='{usr_id}';")
        await connection.execute(
            f"UPDATE pictures SET number={number[0][0]+1}, accept=true WHERE pic_url='{pic_url}'; Commit; "+
            f"UPDATE nickname_id SET count_pics={number[0][0]+1} WHERE usr_id='{usr_id}'; Commit;"
        )

    async def delete_profile(usr_id):
        connection = await asyncpg.connect(
            user=user,
            password=password,
            host=host,
            port=port,
            database=database
        )
        res = await connection.fetch(f"SELECT pic_url FROM pictures WHERE usr_id='{usr_id}';")
        for row in res:
            os.remove(row[0])
        await connection.execute(f"DELETE FROM pictures WHERE usr_id='{usr_id}'; Commit;")
        await connection.execute(f"DELETE FROM nickname_id WHERE usr_id='{usr_id}'; Commit;")
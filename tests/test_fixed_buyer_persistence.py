"""固定买家的收藏持久化、隔离与离线身份迁移。"""
import sqlite3,json
from pathlib import Path
import httpx
from fastapi import FastAPI
from app.infrastructure.buyer_favorites import BuyerFavoriteStore
from app.presentation.favorites import register_favorite_routes
from scripts.migrate_local_buyer import migrate

async def test_favorite_api_persists_after_reopen_and_isolates(tmp_path):
    path=tmp_path/'favorites.db';api=FastAPI()
    register_favorite_routes(api,lambda:BuyerFavoriteStore(path))
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=api),base_url='http://test') as c:
        url='/commerce/favorites/P1001?buyer_id=demo-buyer'
        assert (await c.put(url,json={'product':{'product_id':'P1001','title':'背包'}})).status_code==200
        assert (await c.get('/commerce/favorites?buyer_id=demo-buyer')).json()['products'][0]['title']=='背包'
        assert (await c.get('/commerce/favorites?buyer_id=other')).json()['products']==[]
        await c.delete('/commerce/favorites/P1001?buyer_id=other')
        assert len(await BuyerFavoriteStore(path).list('demo-buyer'))==1
        await c.delete(url)
        assert await BuyerFavoriteStore(path).list('demo-buyer')==[]

def test_migrate_only_selected_identity_keeps_history_and_backup(tmp_path):
    db=sqlite3.connect(tmp_path/'voyacart.db')
    db.execute('CREATE TABLE conversation_sessions(session_id TEXT,buyer_id TEXT)')
    db.executemany('INSERT INTO conversation_sessions VALUES (?,?)',[('s','old'),('test-s','test-buyer')])
    db.execute('CREATE TABLE agent_session_states(session_id TEXT,state_json TEXT)')
    db.execute('INSERT INTO agent_session_states VALUES (?,?)',('s',json.dumps({'name':'old','content':'旧账号 old 的文字不改'})))
    db.commit();db.close()
    report=migrate(tmp_path,'old','demo-buyer')
    with sqlite3.connect(tmp_path/'voyacart.db') as db:
        assert db.execute('SELECT buyer_id FROM conversation_sessions WHERE session_id="s"').fetchone()[0]=='demo-buyer'
        assert db.execute('SELECT buyer_id FROM conversation_sessions WHERE session_id="test-s"').fetchone()[0]=='test-buyer'
        state=json.loads(db.execute('SELECT state_json FROM agent_session_states').fetchone()[0])
        assert state=={'name':'demo-buyer','content':'旧账号 old 的文字不改'}
    assert (tmp_path/'backups').exists() and report['tables']['voyacart.db/conversation_sessions']==1

def test_migrate_covers_model_preferences_and_shopping_forms(tmp_path):
    models=tmp_path/'models.sqlite3';db=sqlite3.connect(models)
    db.execute('CREATE TABLE model_profiles(profile_id TEXT,revision INTEGER,buyer_id TEXT,profile_json TEXT)')
    db.executemany('INSERT INTO model_profiles VALUES (?,?,?,?)',[('preset',1,'*','{}'),('mine',1,'old-buyer','{}')])
    db.execute('CREATE TABLE model_display_preferences(buyer_id TEXT,profile_id TEXT,preferences_json TEXT)')
    db.execute('INSERT INTO model_display_preferences VALUES (?,?,?)',('old-buyer','mine','{}'))
    db.commit();db.close();models.chmod(0o600)
    with sqlite3.connect(tmp_path/'shopping_forms.db') as db:
        db.execute('CREATE TABLE shopping_forms(id TEXT,buyer TEXT,session TEXT,body TEXT)')
        db.execute('INSERT INTO shopping_forms VALUES (?,?,?,?)',('f','old-buyer','s','{}'))
    report=migrate(tmp_path,'old-buyer','demo-buyer')
    with sqlite3.connect(models) as db:
        assert db.execute('SELECT profile_id,buyer_id FROM model_profiles ORDER BY profile_id').fetchall()==[('mine','demo-buyer'),('preset','*')]
        assert db.execute('SELECT buyer_id FROM model_display_preferences').fetchone()[0]=='demo-buyer'
    with sqlite3.connect(tmp_path/'shopping_forms.db') as db:
        assert db.execute('SELECT buyer FROM shopping_forms').fetchone()[0]=='demo-buyer'
    assert report['tables']=={'models.sqlite3/model_profiles':1,'models.sqlite3/model_display_preferences':1,'shopping_forms.db/shopping_forms':1}
    assert (Path(report['backup'])/'models.sqlite3').stat().st_mode&0o777==0o600

# coding: utf-8

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
import time, uuid, functools, threading
from finallogger import logger


def next_id(t=None):
    '''
    Return next id as 50-char string.

    Args:
        t: unix timestamp, default to None and using time.time().
    '''
    if t is None:
        t = time.time()
    return '%015d%s000' % (int(t * 1000), uuid.uuid4().hex)


def _profiling(start, sql=''):
    t = time.time() - start
    if t > 0.1:
        logger.warning('[PROFILING] [DB] %s: %s' % (t, sql))
    else:
        logger.info('[PROFILING] [DB] %s: %s' % (t, sql))


class DBError(Exception):
    pass


class MultiColumnsError(DBError):
    pass


class _LasyConnection(object):
    def __init__(self):
        self._session = None

    def session(self):
        if self._session is None:
            DBSession = sessionmaker(bind=engine)
            self._session = DBSession()
        return self._session

    def commit(self):
        self._session.commit()

    def rollback(self):
        self._session.rollback()

    def cleanup(self):
        if self._session:
            session = self._session
            self._session = None
            logger.info('close connection <%s>...' % hex(id(connection)))
            session.close()


class _DbCtx(threading.local):
    """
    # 持有数据库连接的上下文对象:
    """

    def __init__(self):
        self.connection = None
        self.transactions = 0

    def is_init(self):
        return self.connection

    def init(self):
        logger.info('open lazy connection...')
        self.connection = _LasyConnection()
        self.transactions = 0

    def cleanup(self):
        self.connection.cleanup()
        self.connection = None

    def session(self):
        return self.connection.session()


# thread-local db context:
# _db_ctx是threadlocal对象，所以，它持有的数据库连接对于每个线程看到的都是不一样的。任何一个线程都无法访问到其他线程持有的数据库连接。
_db_ctx = _DbCtx()


class _ConnectionCtx(object):
    """
    因为_DbCtx实现了连接的 获取和释放，但是并没有实现连接
    的自动获取和释放，_ConnectCtx在 _DbCtx基础上实现了该功能，
    因此可以对 _ConnectCtx 使用with 语法，比如：
    with connection():
        pass
        with connection():
            pass
    """

    def __enter__(self):
        global _db_ctx
        self.should_cleanup = False
        if _db_ctx.is_init() is None:
            _db_ctx.init()
            self.should_cleanup = True
        return self

    def __exit__(self, exctype, excvalue, traceback):
        global _db_ctx
        if self.should_cleanup:
            _db_ctx.cleanup()


def connection():
    """
    Connection对象是存储在_DbCtx这个threadlocal对象里的，
    因此，嵌套使用with connection()也没有问题。_DbCtx永远检测当前是否已存在Connection，如果存在，直接使用，如果不存在，则打开一个新的Connection。
    :return:
    """
    return _ConnectionCtx()


# 如果要在一个数据库连接里执行多个SQL语句怎么办？我们用一个with语句实现：
#
# with db.connection():
#     db.select('...')
#     db.update('...')
#     db.update('...')

def with_connection(func):
    @functools.wraps(func)
    def _wrapper(*args, **kw):
        with connection():
            return func(*args, **kw)

    return _wrapper


class _TransactionCtx(object):
    """
    事务也可以嵌套，内层事务会自动合并到外层事务中，这种事务模型足够满足99%的需求。

    事务嵌套比Connection嵌套复杂一点，因为事务嵌套需要计数，每遇到一层嵌套就+1，离开一层嵌套就-1，最后到0时提交事务：
    """

    def __enter__(self):
        global _db_ctx
        self.should_close_conn = False
        if not _db_ctx.is_init():
            # needs open a connection first:
            _db_ctx.init()
            self.should_close_conn = True
        _db_ctx.transactions = _db_ctx.transactions + 1
        logger.info('begin transaction...' if _db_ctx.transactions == 1 else 'join current transaction...')
        return self

    def __exit__(self, exctype, excvalue, traceback):
        global _db_ctx
        _db_ctx.transactions = _db_ctx.transactions - 1
        try:
            if _db_ctx.transactions == 0:
                if exctype is None:
                    self.commit()
                else:
                    self.rollback()
        finally:
            if self.should_close_conn:
                _db_ctx.cleanup()

    def commit(self):
        global _db_ctx
        logger.info('commit transaction...')
        try:
            _db_ctx.connection.commit()
            logger.info('commit ok.')
        except:
            logger.warning('commit failed. try rollback...')
            _db_ctx.connection.rollback()
            logger.warning('rollback ok.')
            raise

    def rollback(self):
        global _db_ctx
        logger.warning('rollback transaction...')
        _db_ctx.connection.rollback()
        logger.info('rollback ok.')


def transaction():
    return _TransactionCtx()


# 如果要在一个数据库事务中执行多个SQL语句怎么办？我们还是用一个with语句实现：
#
# with db.transaction():
#     db.select('...')
#     db.update('...')
#     db.update('...')

def with_transaction(func):
    @functools.wraps(func)
    def _wrapper(*args, **kw):
        _start = time.time()
        with _TransactionCtx():
            func(*args, **kw)
        _profiling(_start)

    return _wrapper


# global engine object:
engine = None


def build_engine(connect_string, database_type='oracle'):
    parameters = database_type is "oracle" and \
                 {"echo": False, "arraysize": 50,
                  "coerce_to_unicode": True} or \
                 database_type is "mysql" and {"echo": False}
    global engine
    if engine is not None:
        logger.info("Create new engine!")
        # raise DBError("Engine is already initialized.")
    engine = create_engine(connect_string, **parameters)


def _find(*query_obj, **filters):
    global _db_ctx
    session = None
    try:
        session = _db_ctx.session()
        sql = session.query(*query_obj)
        if filters:
            sql = sql.filter_by(**filters)
        return sql
    finally:
        if session:
            session.close()


@with_connection
def get(query_obj, indent):
    """
    根据主键值indent条件查询数据库表的记录
    my_user = get(User,5)
    :param query_obj:
    :param indent:
    :return:
    """
    return _find(query_obj).get(indent)


@with_connection
def find_first(*query_obj, **filters):
    """
    根据条件查询数据库表的第一条记录
    find_first(Actor.id,Actor.aid,cellphone=13381712936)
    id = actor.id
    aid = actor.aid
    :param query_obj:
    :param filters:
    :return:
    """
    return _find(*query_obj, **filters).first()


@with_connection
def find_all(*query_obj, **filters):
    """
    根据条件查询数据库表的所有记录
    actor = find_all(Actor.id,Actor.aid,cellphone=13381712936)
    for ac in actor:
        id = ac.id
        aid =ac.aid
    :return:
    """
    return _find(*query_obj, **filters).all()


@with_connection
def find_one(*query_obj, **filters):
    """
    根据条件查询数据库表的所有记录
    find_one(Actor.id,Actor.aid,cellphone=13381712936)
    id = actor.id
    aid = actor.aid
    """
    return _find(*query_obj, **filters).one()


@with_connection
def get_count(*query_obj, **filters):
    """
    根据条件查询数据库表的记录数
    get_count(Actor.id,Actor.aid,cellphone=13381712936)
    id = actor.id
    aid = actor.aid
    """
    return _find(*query_obj, **filters).count()


@with_connection
def get_max(*query_obj, **filters):
    global _db_ctx
    session = None
    try:
        session = _db_ctx.session()
        sql = session.query(func.max(*query_obj))
        if filters:
            sql = sql.filter_by(**filters)
        return sql.one()
    finally:
        if session:
            session.close()


@with_connection
def update(table_model, update_columns, **filters):
    """
    update(Addr, dict(state=state, city=city), aid=aid)
    :param table_model:
    :param update_columns:
    :param filters:
    :return:
    """
    global _db_ctx
    session = None
    try:
        session = _db_ctx.connection.session()
        r = session.query(table_model).filter_by(**filters).update(update_columns, synchronize_session='fetch')
        if _db_ctx.transactions == 0:
            # no transaction enviroment:
            _db_ctx.connection.commit()
            logger.info('update {} set {} where {} success'.format(table_model.__name__, update_columns, filters))
        return r
    finally:
        if session:
            session.close()


@with_connection
def delete(table_model, **filters):
    if not filters:
        raise Exception("Please provide valid filters.")
    global _db_ctx
    session = None
    try:
        session = _db_ctx.connection.session()
        r = session.query(table_model).filter_by(**filters).delete()
        if _db_ctx.transactions == 0:
            # no transaction enviroment:
            logger.info('delete {} where {} success'.format(table_model.__name__, filters))
            _db_ctx.connection.commit()
        return r
    finally:
        if session:
            session.close()


@with_connection
def insert(table_model, **filters):
    """
    insert(Facereconresult, id=face_id, userid=aid, pairverifyresultmin=0,
            pairverifyresult=1, pairverifysimilarity=88,
            timeinfo=datetime.datetime.now(), facereconstatus='PASSED')
    :param table_model:
    :param filters:
    :return:
    """
    if not filters:
        raise Exception("Please provide valid filters.")
    global _db_ctx
    session = None
    try:
        session = _db_ctx.connection.session()
        record = table_model(**filters)
        session.add(record)
        if _db_ctx.transactions == 0:
            # no transaction enviroment:
            logger.info('insert {} where {} success'.format(table_model.__name__, filters))
            _db_ctx.connection.commit()
    finally:
        if session:
            session.close()

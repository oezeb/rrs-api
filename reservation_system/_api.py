from flask import Blueprint, request
from flask.views import MethodView as MethodView
from marshmallow import fields, Schema
from webargs.flaskparser import use_kwargs

from reservation_system import db
from reservation_system.models import schemas
from reservation_system.util import marshal_with

def init_api(app, spec):
    for path, view in (
        ('reservations'              , Reservations  ),
        ('reservations/status'       , ResvStatus    ),
        ('reservations/privacy'      , ResvPrivacy   ),
        ('users'                     , Users         ),
        ('users/roles'               , UserRoles     ),
        ('rooms'                     , Rooms         ),
        ('rooms/types'               , RoomTypes     ),
        ('rooms/status'              , RoomStatus    ),
        ('languages'                 , Languages     ),
        ('sessions'                  , Sessions      ),
        ('notices'                   , Notices       ),
        ('periods'                   , Periods       ),
        ('settings'                  , Settings      ),
        # translations
    ): register_view(app, spec, path, view)

def register_view(app, spec, path, view):
    url = f'/api/{path}'
    method_view = view.as_view(path)

    app.add_url_rule(url, view_func=method_view)

    with app.test_request_context():
        spec.path(view=method_view)

class Reservations(MethodView):
    class GetReservationsQuerySchema(schemas.ReservationSchema):
        start_date = fields.Date()
        end_date = fields.Date()
        create_date = fields.Date()
        update_date = fields.Date()

    @use_kwargs(GetReservationsQuerySchema(), location='query')
    @marshal_with(schemas.ManyReservationSchema(), code=200)
    def get(self, start_date=None, end_date=None, create_date=None, update_date=None, **kwargs):
        """Get reservations
        ---
        summary: Get reservations
        description: Get reservations
        tags:
          - Public
        parameters:
          - in: query
            schema: GetReservationsQuerySchema
        responses:
          200:
            description: Success(OK)
            content:
              application/json:
                schema: ManyReservationSchema
        """
        if start_date:  kwargs['DATE(start_time)']  = '%s' % start_date
        if end_date:    kwargs['DATE(end_time)']    = '%s' % end_date
        if create_date: kwargs['DATE(create_time)'] = '%s' % create_date
        if update_date: kwargs['DATE(update_time)'] = '%s' % update_date

        res = db.select(db.Reservation.TABLE, order_by=['start_time', 'end_time'], **kwargs)
        # check privacy
        for r in res:
            if r['privacy'] == db.ResvPrivacy.ANONYMOUS:
                r.pop('username')
            if r['privacy'] == db.ResvPrivacy.PRIVATE:
                r = {
                    'start_time': r['start_time'],
                    'end_time': r['end_time'],
                    'status': r['status'],
                    'room_id': r['room_id'],
                }
        return res

class Users(MethodView):
    class UsersGetQuerySchema(Schema):
        username = fields.Str()
        name = fields.Str()
    
    class UsersGetResponseSchema(schemas.Many, UsersGetQuerySchema):
        pass
            
    @use_kwargs(UsersGetQuerySchema(), location='query')
    @marshal_with(UsersGetResponseSchema(), code=200)
    def get(self, **kwargs):
        """Get users
        ---
        summary: Get users
        description: Get users
        tags:
          - Public
        parameters:
          - in: query
            schema: UsersGetQuerySchema
        responses:
          200:
            description: OK
            content:
              application/json:
                schema: UsersGetResponseSchema
        """
        return db.select(db.User.TABLE, **kwargs)

class Rooms(MethodView):
    class RoomsGetQuerySchema(schemas.RoomSchema):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, exclude=('image',), **kwargs)

    @use_kwargs(RoomsGetQuerySchema(), location='query')
    @marshal_with(schemas.ManyRoomSchema(), code=200)
    def get(self, **kwargs):
        """Get rooms
        ---
        summary: Get rooms
        description: Get rooms
        tags:
          - Public
        parameters:
          - in: query
            schema: RoomsGetQuerySchema
        responses:
          200:
            description: OK
            content:
              application/json:
                schema: ManyRoomSchema
        """
        return db.select(db.Room.TABLE, **kwargs)
       
class Periods(MethodView):
    @use_kwargs(schemas.PeriodSchema(), location='query')
    @marshal_with(schemas.ManyPeriodSchema(), code=200)
    def get(self, **kwargs):
        """Get periods
        ---
        summary: Get periods
        description: Get periods
        tags:
          - Public
        parameters:
          - in: query
            schema: PeriodSchema
        responses:
          200:
            description: OK
            content:
              application/json:
                schema: ManyPeriodSchema
        """
        return db.select(db.Period.TABLE, **kwargs)

class Notices(MethodView):
    @use_kwargs(schemas.NoticeSchema(), location='query')
    @marshal_with(schemas.ManyNoticeSchema(), code=200)
    def get(self, **kwargs):
        """Get notices
        ---
        summary: Get notices
        description: Get notices
        tags:
          - Public
        parameters:
          - in: query
            schema: NoticeSchema
        responses:
          200:
            description: OK
            content:
              application/json:
                schema: ManyNoticeSchema
        """
        return db.select(db.Notice.TABLE, order_by=['create_time', 'update_time'], **kwargs)

class Sessions(MethodView):
    @use_kwargs(schemas.SessionSchema(), location='query')
    @marshal_with(schemas.ManySessionSchema(), code=200)
    def get(self, **kwargs):
        """Get sessions
        ---
        summary: Get sessions
        description: Get sessions
        tags:
          - Public
        parameters:
          - in: query
            schema: SessionSchema
        responses:
          200:
            description: OK
            content:
              application/json:
                schema: ManySessionSchema
        """
        return db.select(db.Session.TABLE, **kwargs)   

class RoomTypes(MethodView):
    @use_kwargs(schemas.RoomTypeSchema(), location='query')
    @marshal_with(schemas.ManyRoomTypeSchema(), code=200)
    def get(self, **kwargs):
        """Get room types
        ---
        summary: Get room types
        description: Get room types
        tags:
          - Public
        parameters:
          - in: query
            schema: RoomTypeSchema
        responses:
          200:
            description: OK
            content:
              application/json:
                schema: ManyRoomTypeSchema
        """
        return db.select(db.RoomType.TABLE, **kwargs)

class Languages(MethodView):
    @use_kwargs(schemas.LanguageSchema(), location='query')
    @marshal_with(schemas.ManyLanguageSchema(), code=200)
    def get(self, **kwargs):
        """Get languages
        ---
        summary: Get languages
        description: Get languages
        tags:
          - Public
        parameters:
          - in: query
            schema: LanguageSchema
        responses:
          200:
            description: OK
            content:
              application/json:
                schema: ManyLanguageSchema
        """
        return db.select(db.Language.TABLE, **kwargs)
    
class ResvStatus(MethodView):
    @use_kwargs(schemas.ResvStatusSchema(), location='query')
    @marshal_with(schemas.ManyResvStatusSchema(), code=200)
    def get(self, **kwargs):
        """Get reservation status
        ---
        summary: Get reservation status
        description: Get reservation status
        tags:
          - Public
        parameters:
          - in: query
            schema: ResvStatusSchema
        responses:
          200:
            description: OK
            content:
              application/json:
                schema: ManyResvStatusSchema
        """
        return db.select(db.ResvStatus.TABLE, **kwargs)
    
class ResvPrivacy(MethodView):
    @use_kwargs(schemas.ResvPrivacySchema(), location='query')
    @marshal_with(schemas.ManyResvPrivacySchema(), code=200)
    def get(self, **kwargs):
        """Get reservation privacy
        ---
        summary: Get reservation privacy
        description: Get reservation privacy
        tags:
          - Public
        parameters:
          - in: query
            schema: ResvPrivacySchema
        responses:
          200:
            description: OK
            content:
              application/json:
                schema: ManyResvPrivacySchema
        """
        return db.select(db.ResvPrivacy.TABLE, **kwargs)
    
class RoomStatus(MethodView):
    @use_kwargs(schemas.RoomStatusSchema(), location='query')
    @marshal_with(schemas.ManyRoomStatusSchema(), code=200)
    def get(self, **kwargs):
        """Get room status
        ---
        summary: Get room status
        description: Get room status
        tags:
          - Public
        parameters:
          - in: query
            schema: RoomStatusSchema
        responses:
          200:
            description: OK
            content:
              application/json:
                schema: ManyRoomStatusSchema
        """
        return db.select(db.RoomStatus.TABLE, **kwargs)
    
class UserRoles(MethodView):
    @use_kwargs(schemas.UserRoleSchema(), location='query')
    @marshal_with(schemas.ManyUserRoleSchema(), code=200)
    def get(self, **kwargs):
        """Get user roles
        ---
        summary: Get user roles
        description: Get user roles
        tags:
          - Public
        parameters:
          - in: query
            schema: UserRoleSchema
        responses:
          200:
            description: OK
            content:
              application/json:
                schema: ManyUserRoleSchema
        """
        return db.select(db.UserRole.TABLE, **kwargs)

class Settings(MethodView):
    @use_kwargs(schemas.SettingSchema(), location='query')
    @marshal_with(schemas.ManySettingSchema(), code=200)
    def get(self, **kwargs):
        """Get settings
        ---
        summary: Get settings
        description: Get settings
        tags:
          - Public
        parameters:
          - in: query
            schema: SettingSchema
        responses:
          200:
            description: OK
            content:
              application/json:
                schema: ManySettingSchema
        """
        return db.select(db.Setting.TABLE, **kwargs)

from marshmallow import Schema, fields


class ReviewSchema(Schema):
    id = fields.String(required=True)
    titlu = fields.String(required=True)
    comentariu = fields.String(required=True)
    nota = fields.Integer(required=True)
    nume = fields.String(required=True)


class RadioCodeSchema(Schema):
    vin = fields.String(required=True)
    serie = fields.String(dump_only=True)
    marca = fields.String(dump_only=True)
    radio_code = fields.List(fields.String(), dump_only=True)


class TrustPilotReviewsSchema(Schema):
    domeniu = fields.String(required=True)
    toal_reviews = fields.Integer(dump_only=True)
    reviews = fields.List(fields.Nested(ReviewSchema()), dump_only=True)

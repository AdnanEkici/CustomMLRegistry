from __future__ import annotations

import random
from typing import Final

from marshmallow import fields
from marshmallow import Schema
from marshmallow import validate


class ModelInputSchema(Schema):
    GENDER_LIST: Final = ["Female", "Male"]

    customer_id = fields.Integer(required=True)
    age = fields.Integer(required=False, validate=validate.Range(min=0), missing=0)
    gender = fields.String(required=False, validate=validate.OneOf(GENDER_LIST), missing=random.choice(GENDER_LIST))
    annual_income = fields.Integer(required=False, validate=validate.Range(min=0), missing=0)
    purchase_amount = fields.Float(required=True)
    purchase_date = fields.String(required=True)
    next_month_purchase_amount = fields.Float(allow_none=True)

# schemas/recipe.py file

# Import the necessary package and module
from flask import request
from marshmallow import Schema, fields
from urllib.parse import urlencode


class PaginationSchema(Schema):

    class Meta:
        ordered = True

    # Serialize the pagination object from Flask-SQLAlchemy
    links = fields.Method(serialize='get_pagination_links')
    page = fields.Integer(dump_only=True)
    pages = fields.Integer(dump_only=True)
    per_page = fields.Integer(dump_only=True)
    total = fields.Integer(dump_only=True)

    @staticmethod
    def get_url(page):
        """This method has got the logic to generate the URL of the page based on
        the page number"""
        query_args = request.args.to_dict()
        query_args['page'] = page

        # Encodes and returns the new URL
        return '{}?{}'.format(request.base_url, urlencode(query_args))

    def get_pagination_links(self, paginated_objects):
        """This method has got the logic to generate URL links to different pages"""
        pagination_links = {
            'first': self.get_url(page=1),
            'last': self.get_url(page=paginated_objects.pages)
        }

        if paginated_objects.has_prev:
            pagination_links['prev'] = self.get_url(page=paginated_objects.prev_num)

        if paginated_objects.has_next:
            pagination_links['next'] = self.get_url(page=paginated_objects.next_num)

        return pagination_links

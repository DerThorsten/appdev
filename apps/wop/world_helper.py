from Box2D import *

class FindBodyQueryCallback(Box2D.b2QueryCallback):
    def __init__(self, p): 
        super(FindBodyQueryCallback, self).__init__()
        self.point = p
        self.fixture = None

    def ReportFixture(self, fixture):
        body = fixture.body
        if body.type == b2_dynamicBody:
            inside=fixture.TestPoint(self.point)
            if inside:
                self.fixture=fixture
                # We found the object, so stop the query
                return False
        # Continue the query
        return True


def body_at_pos(world, pos, roiSize = 0.0001, filter=None):
    p = b2Vec2(*pos)
    query = FindBodyQueryCallback(p)
    aabb = b2AABB(lowerBound=p-(0.001, 0.001), upperBound=p+(0.001, 0.001))
    world.QueryAABB(query, aabb)
    return query.fixture

def bodies_in_rio(world, roi, getDist=False, filter=None):
    pass

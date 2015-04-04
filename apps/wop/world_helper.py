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
            self.fixture=fixture
            #return False
            if inside:
                self.fixture=fixture
                # We found the object, so stop the query
                return False
        # Continue the query
        return True

class FindBodyInBoundigBox(Box2D.b2QueryCallback):
    def __init__(self, p): 
        super(FindBodyInBoundigBox, self).__init__()
        self.point = p
        self.fixture = None
    def ReportFixture(self, fixture):
        body = fixture.body
        if body.type == b2_dynamicBody:
            inside=fixture.TestPoint(self.point)
            self.fixture=fixture
            return False
        # Continue the query
        return True


class FindAllInBoundigBox(Box2D.b2QueryCallback):
    def __init__(self): 
        super(FindBodyInBoundigBox, self).__init__()
        self.bodies = set()
    def ReportFixture(self, fixture):
        body = fixture.body
        if body.type == b2_dynamicBody:
            inside=fixture.TestPoint(self.point)
            self.bodies.insert(fixture.body)
        # Continue the query
        return True

def all_bodies_in_bb(world, pos, roiRadius = 0.0001, filter=None):
    p = b2Vec2(*pos)
    query = FindAllInBoundigBox()
    aabb = b2AABB(lowerBound=p-(roiRadius, roiRadius), upperBound=p+(roiRadius, roiRadius))
    world.QueryAABB(query, aabb)
    return query.bodies

def body_in_bb(world, pos, roiRadius = 0.0001, filter=None):
    p = b2Vec2(*pos)
    query = FindBodyInBoundigBox(p)
    aabb = b2AABB(lowerBound=p-(roiRadius, roiRadius), upperBound=p+(roiRadius, roiRadius))
    world.QueryAABB(query, aabb)
    if query.fixture is None:
        return None
    else:
        return query.fixture.body

def body_at_pos(world, pos, roiRadius = 0.0001, filter=None):
    p = b2Vec2(*pos)
    query = FindBodyQueryCallback(p)
    aabb = b2AABB(lowerBound=p-(roiRadius, roiRadius), upperBound=p+(roiRadius, roiRadius))
    world.QueryAABB(query, aabb)
    if query.fixture is None:
        return None
    else:
        return query.fixture.body

def bodies_in_rio(world, roi, getDist=False, filter=None):
    pass

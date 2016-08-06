import pybox2d as b2

class FindBodyQueryCallback(b2.QueryCallback):
    def __init__(self, p): 
        super(FindBodyQueryCallback, self).__init__()
        self.point = p
        self.fixture = None

    def ReportFixture(self, fixture):
        body = fixture.body
        if body.btype == b2.BodyTypes.dynamicBody:
            inside=fixture.testPoint(self.point)
            #return False
            #print "found a body in bounding box"
            if inside:
                self.fixture=fixture
                # We found the object, so stop the query
                #print "    -click is inside"
                return False
        # Continue the query
        return True

class FindBodyInBoundigBox(b2.QueryCallback):
    def __init__(self, p): 
        super(FindBodyInBoundigBox, self).__init__()
        self.point = p
        self.fixture = None
    def ReportFixture(self, fixture):
        body = fixture.body
        if body.btype == b2.BodyTypes.dynamicBody:
            inside=fixture.testPoint(self.point)
            self.fixture=fixture
            return False
        # Continue the query
        return True


class FindAllInBoundigBox(b2.QueryCallback):
    def __init__(self): 
        super(FindBodyInBoundigBox, self).__init__()
        self.bodies = set()
    def ReportFixture(self, fixture):
        body = fixture.body
        if body.btype == b2.BodyTypes.dynamicBody:
            inside=fixture.testPoint(self.point)
            self.bodies.insert(fixture.body)
        # Continue the query
        return True

def all_bodies_in_bb(world, pos, roiRadius = 0.0001, filter=None):
    p = b2.vec2(*pos)
    query = FindAllInBoundigBox()
    aabb = b2.aabb(lowerBound=p-(roiRadius, roiRadius), upperBound=p+(roiRadius, roiRadius))
    world.QueryAABB(query, aabb)
    return query.bodies

def body_in_bb(world, pos, roiRadius = 0.0001, filter=None):
    p = b2.vec2(*pos)
    query = FindBodyInBoundigBox(p)
    aabb = b2.aabb(lowerBound=p-(roiRadius, roiRadius), upperBound=p+(roiRadius, roiRadius))
    world.QueryAABB(query, aabb)
    if query.fixture is None:
        return None
    else:
        return query.fixture.body

def body_at_pos(world, pos, roiRadius = 0.0001, filter=None):
    p = b2.vec2(*pos)
    query = FindBodyQueryCallback(p)
    aabb = b2.aabb(lowerBound=p-b2.vec2(roiRadius, roiRadius), upperBound=p+b2.vec2(roiRadius, roiRadius))
    world.queryAABB(query, aabb)
    if query.fixture is None:
        return None
    else:
        return query.fixture.body

def bodies_in_rio(world, roi, getDist=False, filter=None):
    pass

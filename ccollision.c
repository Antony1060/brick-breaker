#define PY_SSIZE_T_CLEAN
#include<python3.10/Python.h>

#include<stdbool.h>
#include<math.h>
#include<stddef.h>
#include<stdlib.h>
#include<stdio.h>

#define TOP 0
#define RIGHT 1
#define BOTTOM 2
#define LEFT 3

#define LOG(x) printf(#x ": %d | ", x);
#define FNL printf("\n"); fflush(stdout);

#define logN(n) printf(#n); FNL

//
// Note: this file is more of a joke than a serieous optimization
//

typedef struct Point {
    double x, y;
} Point;

typedef struct Slope {
    double k, l;
} Slope;

typedef struct Rect {
    int x, y;
    int width, height;
    Point points[4];
    Slope slopes[4];
} Rect;

typedef struct CollisionReturn {
    const char *side;
    Point point;
} CollisionReturn;

const char* to_side_str(int code) {
    switch (code) {
        case TOP:
            return "top";
        case BOTTOM:
            return "bottom";
        case LEFT:
            return "left";
        case RIGHT:
            return "right";
        default:
            return "";
    }
}

bool num_between(double num, double bound1, double bound2) {
    return ((bound1 - num) * (bound2 - num)) <= 0;
}

// returns true when the two are not colliding
bool __outside_collidable(int c_x, int c_y, int c_r, Rect* rect) {
    long diff_x = abs(c_x - (rect->x + rect->width / 2));
    long diff_y = abs(c_y - (rect->y + rect->height / 2));

    return c_r + rect->width / 2 < diff_x && c_r + rect->height / 2 < diff_y;
}

uint8_t slope_intersection(int c_x, int c_y, int c_r, Slope slope, Point points[2]) {
    double k = slope.k;
    double l = slope.l;

    int p = c_x;
    int q = c_y;
    int r = c_r;

    double psq = p * p;
    double qsq = q * q;
    double rsq = r * r;
    double ksq = k * k;
    double lsq = l * l;

    double under_root = -ksq * psq + ksq * rsq - 2 * k * l * p + 2 * k * p * q - lsq + 2 * l * q - qsq + rsq;
    if (under_root < 0)
        return 1;
    
    double raw_root = sqrt(under_root);

    double x1 = (-raw_root - k * l + k * q + p) / (ksq + 1);
    double x2 = (raw_root - k * l + k * q + p) / (ksq + 1);

    double y1 = x1 * k + l;
    double y2 = x2 * k + l;

    points[0].x = x1;
    points[0].y = y1;
    points[1].x = x2;
    points[1].y = y2;

    return 0;
}

CollisionReturn* allocate_return(int side) {
    CollisionReturn *ret = (CollisionReturn*) malloc(sizeof(CollisionReturn));
    ret->side = to_side_str(side);
    return ret;
}

CollisionReturn* detect_collision(int c_x, int c_y, int c_r, Rect* rect) {
    if(__outside_collidable(c_x, c_y, c_r, rect))
        return NULL;

    int i;
    for(i = 0; i < 4; ++i) {
        Slope slope = rect->slopes[i];

        Point intersections[2];
        int fail = slope_intersection(c_x, c_y, c_r, slope, intersections);
        if(fail)
            continue;

        Point inter_point1 = intersections[0];
        Point inter_point2 = intersections[1];

        Point p1 = rect->points[i];
        Point p2 = rect->points[(i + 1) % 4];

        if(i == TOP || i == BOTTOM) {
            if(num_between(inter_point1.x, p1.x, p2.x)) {
                CollisionReturn* ret = allocate_return(i);
                ret->point = inter_point1;
                return ret;
            } else if(num_between(inter_point2.x, p1.x, p2.x)) {
                CollisionReturn* ret = allocate_return(i);
                ret->point = inter_point2;
                return ret;
            }
        } else {
            if(num_between(inter_point1.y, p1.y, p2.y)) {
                CollisionReturn* ret = allocate_return(i);
                ret->point = inter_point1;
                return ret;
            } else if(num_between(inter_point2.y, p1.y, p2.y)) {
                CollisionReturn* ret = allocate_return(i);
                ret->point = inter_point2;
                return ret;
            }
        }
    }

    return NULL;
}

PyObject* ccollision_detect_collision(PyObject* self, PyObject* args) {
    int c_x, c_y, c_r;
    Rect* r = malloc(sizeof(Rect));

    // format for (circle_x, circle_y, circle_radius), (rect_x, rect_y, rect_width, rect_height), (x_1, y_1, x_2, y_2), (s1k, s1l, ..., s4k, s4l)
    // third tuple is used for point coordinates, explanation: https://media.antony.red/bBUvGA.png
    if(!PyArg_ParseTuple(
            args, "(iii)(iiii)(dddd)(dddddddd)", &c_x, &c_y, &c_r,
            &r->x, &r->y, &r->width, &r->height,
            &r->points[0].x, &r->points[0].y, &r->points[2].x, &r->points[2].y,
            &r->slopes[0].k, &r->slopes[0].l, &r->slopes[1].k, &r->slopes[1].l, &r->slopes[2].k, &r->slopes[2].l, &r->slopes[3].k, &r->slopes[3].l
        ))
        return NULL;
    
    // adjust leftover points
    r->points[1].x = r->points[2].x;
    r->points[1].y = r->points[0].y;
    r->points[3].x = r->points[0].x;
    r->points[3].y = r->points[2].y;

    CollisionReturn* res = detect_collision(c_x, c_y, c_r, r);
    if(res == NULL)
        Py_RETURN_NONE;

    PyObject* return_tuple = Py_BuildValue("sdd", res->side, res->point.x, res->point.y);

    free(r);

    return return_tuple;
}

static PyMethodDef CCollisionMethods[] = {
    {"detect_collision", ccollision_detect_collision, METH_VARARGS, "Calculate the colliding points of a circle and a rectangle"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef ccollisionmodule = {
    PyModuleDef_HEAD_INIT,
    "ccollision",
    NULL,
    -1,
    CCollisionMethods
};

PyMODINIT_FUNC PyInit_ccollision(void) {
    return PyModule_Create(&ccollisionmodule);
}
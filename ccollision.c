#define PY_SSIZE_T_CLEAN
#include<python3.10/Python.h>

#include<stdbool.h>
#include<math.h>
#include<stddef.h>
#include<stdlib.h>
#include<stdio.h>

#define TOP 0
#define BOTTOM 1
#define LEFT 2
#define RIGHT 3

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
    long x, y;
    long width, height;
    Point* points[4][2];
    Slope* slopes[4];
} Rect;

typedef struct CollisionReturn {
    char *side;
    Point* point;
} CollisionReturn;

char* to_side_str(int code) {
    switch (code) {
        case 0:
            return "top";
        case 1:
            return "bottom";
        case 2:
            return "left";
        case 3:
            return "right";
    }
}

bool num_between(double num, double bound1, double bound2) {
    return ((bound1 - num) * (bound2 - num)) <= 0;
}

// returns true when the two are not colliding
bool __outside_collidable(long c_x, long c_y, long c_r, Rect* rect) {
    long diff_x = abs(c_x - (rect->x + rect->width / 2));
    long diff_y = abs(c_y - (rect->y + rect->height / 2));

    return c_r + rect->width / 2 < diff_x && c_r + rect->height / 2 < diff_y;
}

uint8_t slope_intersection(long c_x, long c_y, long c_r, Slope* slope, Point* points[2]) {
    double k = slope->k;
    double l = slope->l;

    long p = c_x;
    long q = c_y;
    long r = c_r;

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

    points[0]->x = x1;
    points[0]->y = y1;
    points[1]->x = x2;
    points[1]->y = y2;

    return 0;
}

CollisionReturn* allocate_return(int side) {
    CollisionReturn *ret = (CollisionReturn*) malloc(sizeof(CollisionReturn));
    ret->side = to_side_str(side);
    return ret;
}

CollisionReturn* detect_collision(long c_x, long c_y, long c_r, Rect* rect) {
    if(__outside_collidable(c_x, c_y, c_r, rect))
        return NULL;

    int i;
    for(i = 0; i < 4; ++i) {
        Slope* slope = rect->slopes[i];

        Point* intersections[2];
        int fail = slope_intersection(c_x, c_y, c_r, slope, intersections);
        if(fail)
            continue;

        Point* inter_point1 = intersections[0];
        Point* inter_point2 = intersections[1];

        Point* p1 = rect->points[i][0];
        Point* p2 = rect->points[i][1];

        if(i < 2) {
            if(num_between(inter_point1->x, p1->x, p2->x)) {
                CollisionReturn* ret = allocate_return(i);
                ret->point = inter_point1;
                return ret;
            } else if(num_between(inter_point2->x, p1->x, p2->x)) {
                CollisionReturn* ret = allocate_return(i);
                ret->point = inter_point2;
                return ret;
            }
        } else {
            if(num_between(inter_point1->y, p1->y, p2->y)) {
                CollisionReturn* ret = allocate_return(i);
                ret->point = inter_point1;
                return ret;
            } else if(num_between(inter_point2->y, p1->y, p2->y)) {
                CollisionReturn* ret = allocate_return(i);
                ret->point = inter_point2;
                return ret;
            }
        }
    }

    return NULL;
}

Rect* convert_pyobject_to_rect(PyObject *pyrect) {
    Rect* rect;

    if(pyrect == NULL) {
        printf("passed null\n");
        fflush(stdout);

        return NULL;
    }

    if(PyObject_Print(pyrect, stdout, 0) != 0) {
        logN(koji kurac);

        return NULL;
    }

    logN(11);
    PyObject* obj = PyObject_GetAttrString(pyrect, "x");
    logN(11);
    if(obj == NULL) {
        logN(9999);
        return NULL;
    }

    rect->x = PyLong_AsLong(PyObject_GetAttrString(pyrect, "x"));
    rect->y = PyLong_AsLong(PyObject_GetAttrString(pyrect, "y"));
    rect->width = PyLong_AsLong(PyObject_GetAttrString(pyrect, "width"));
    rect->height = PyLong_AsLong(PyObject_GetAttrString(pyrect, "height"));

    logN(2);
    int i, j;

    logN(3);
    logN(1000);
    PyObject* point_list = PyObject_GetAttrString(pyrect, "points");
    for(i = 0; i < 4; ++i) {
        logN(i);
        PyObject* point_tuple = PyList_GetItem(point_list, i);
        
        PyObject* point1;
        PyObject* point2;
        if(!PyArg_ParseTuple(point_tuple, "OO", point1, point2))
            return NULL;

        double p1x = PyFloat_AsDouble(PyObject_GetAttrString(point1, "x"));
        double p1y = PyFloat_AsDouble(PyObject_GetAttrString(point1, "y"));
        double p2x = PyFloat_AsDouble(PyObject_GetAttrString(point2, "x"));
        double p2y = PyFloat_AsDouble(PyObject_GetAttrString(point2, "y"));
        LOG(p1x)
        LOG(p1y)
        LOG(p2x)
        LOG(p2y)
        FNL

        rect->points[i][0]->x = p1x;
        rect->points[i][0]->y = p1y;
        rect->points[i][1]->x = p2x;
        rect->points[i][1]->y = p2y;
    }
    logN(1000);

    PyObject* slope_list = PyObject_GetAttrString(pyrect, "slopes");

    logN(4);

    logN(2000);
    for(i = 0; i < 4; ++i) {
        logN(i);
        PyObject* slope = PyList_GetItem(point_list, i);

        double k = PyFloat_AsDouble(PyObject_GetAttrString(slope, "direction_coefficient"));
        double l = PyFloat_AsDouble(PyObject_GetAttrString(slope, "y_shift"));
        LOG(k)
        LOG(l)
        FNL

        rect->slopes[i]->k = k;
        rect->slopes[i]->l = l;
    }
    logN(2000);

    return rect;
}

PyObject* ccollision_detect_collision(PyObject* self, PyObject* args) {
    long c_x, c_y, c_r;
    PyObject* pyrect;

    printf("1");
    FNL
    if(!PyArg_ParseTuple(args, "lllO", &c_x, &c_y, &c_r, pyrect))
        return NULL;

    PyObject_Print(pyrect, stdout, Py_PRINT_RAW);

    printf("2");
    FNL
    LOG(c_x)
    LOG(c_y)
    LOG(c_r)
    FNL    
    Rect* rect = convert_pyobject_to_rect(pyrect);
    assert(rect != NULL);

    printf("3");
    FNL

    CollisionReturn* res = detect_collision(c_x, c_y, c_r, rect);
    if(res == NULL)
        Py_RETURN_NONE;

    printf("4");
    FNL
    PyObject* res_tuple = PyTuple_Pack(3, res->side, res->point->x, res->point->y);
    assert(res_tuple != NULL);

    printf("5");
    FNL;
    return res_tuple;
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
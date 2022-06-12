#include<stdbool.h>
#include<math.h>
#include<stddef.h>
#include<stdlib.h>
#include<stdio.h>

#define TOP 0
#define BOTTOM 1
#define LEFT 2
#define RIGHT 3

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
    Point points[4][2];
    Slope slopes[4];
} Rect;

typedef struct CollisionReturn {
    char *side;
    Point point;
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
bool __outside_collidable(int c_x, int c_y, int c_r, Rect rect) {
    int diff_x = abs(c_x - (rect.x + rect.width / 2));
    int diff_y = abs(c_y - (rect.y + rect.height / 2));

    return c_r + rect.width / 2 < diff_x && c_r + rect.height / 2 < diff_y;
}

int slope_intersection(int c_x, int c_y, int c_r, Slope slope, Point points[2]) {
    double k = slope.k;
    double l = slope.l;

    double p = c_x;
    double q = c_y;
    double r = c_r;

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

CollisionReturn* detect_collision(int c_x, int c_y, int c_r, Rect rect) {
    if(__outside_collidable(c_x, c_y, c_r, rect))
        return NULL;

    int i;
    for(i = 0; i < 4; ++i) {
        Slope slope = rect.slopes[i];

        Point intersections[2];
        int fail = slope_intersection(c_x, c_y, c_r, slope, intersections);
        if(fail)
            continue;

        Point inter_point1 = intersections[0];
        Point inter_point2 = intersections[1];

        Point p1 = rect.points[i][0];
        Point p2 = rect.points[i][1];

        if(i < 2) {
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

void free_mem(void *ptr) {
    free(ptr);
}
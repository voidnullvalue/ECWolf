#!/usr/bin/env python3
"""Numerical regression test for ECWolf's converged stereo camera geometry."""
import math

FOCAL_LENGTH = 0x5700 / 65536.0
PROJECTION_SCALE = 160.0
HALF_EYE_SEPARATION = 8.0 / 256.0
CONVERGENCE_DISTANCE = 16.0 / 4.0


def projected_x(eye_sign, object_depth):
    eye_y = eye_sign * HALF_EYE_SEPARATION
    yaw = eye_sign * math.atan2(HALF_EYE_SEPARATION, CONVERGENCE_DISTANCE)

    forward_x = math.cos(yaw)
    forward_y = -math.sin(yaw)
    right_x = math.sin(yaw)
    right_y = math.cos(yaw)

    focal_x = -FOCAL_LENGTH * forward_x
    focal_y = eye_y - FOCAL_LENGTH * forward_y

    relative_x = object_depth - focal_x
    relative_y = -focal_y
    depth = relative_x * forward_x + relative_y * forward_y
    lateral = relative_x * right_x + relative_y * right_y
    return PROJECTION_SCALE * lateral / depth


def disparity(depth):
    return projected_x(1, depth) - projected_x(-1, depth)


def main():
    near = disparity(1.0)
    convergence = disparity(CONVERGENCE_DISTANCE)
    far = disparity(16.0)

    assert abs(convergence) < 1e-9, convergence
    assert near * far < 0.0, (near, far)
    assert abs(near) > abs(far), (near, far)
    assert len({round(disparity(depth), 6) for depth in (1.0, 2.0, 4.0, 8.0, 16.0)}) == 5

    print('near disparity:        %.6f px' % near)
    print('convergence disparity: %.6f px' % convergence)
    print('far disparity:         %.6f px' % far)
    print('PASS: disparity varies with depth and crosses zero at convergence.')


if __name__ == '__main__':
    main()

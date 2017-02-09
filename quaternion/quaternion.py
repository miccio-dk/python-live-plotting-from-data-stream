# Intended use: rotation
import numbers
import numpy as np


class Quaternion(object):
    def __init__(self, w=1.0, i=0.0, j=0.0, k=0.0):
        self.val = np.array([w, i, j, k])

    def __add__(self, rhs):
        if isinstance(rhs, self.__class__):
            return Quaternion(*self.val + rhs.val)
        elif isinstance(rhs, np.ndarray):
            return Quaternion(*self.val + rhs)
        elif isinstance(rhs, numbers.Number):
            return Quaternion(*self.val[0] + rhs)
        else:
            print("Tried to add unknown type", rhs.__class__ is Quaternion, self.__class__ is Quaternion)

    def __radd__(self, lhs):
        if isinstance(lhs, numbers.Number):
            return self + lhs

    def __sub__(self, rhs):
        if isinstance(rhs, np.ndarray):
            return Quaternion(*(self.val - rhs))
        else:
            return Quaternion(*(self.val - rhs.val))

    def __mul__(self, rhs):
        if isinstance(rhs, Quaternion):
            # Hamilton product
            return Quaternion(self.val[0] * rhs.val[0] - self.val[1] * rhs.val[1] - self.val[2] * rhs.val[2] - self.val[3] * rhs.val[3],
                              self.val[0] * rhs.val[1] + self.val[1] * rhs.val[0] + self.val[2] * rhs.val[3] - self.val[3] * rhs.val[2],
                              self.val[0] * rhs.val[2] - self.val[1] * rhs.val[3] + self.val[2] * rhs.val[0] + self.val[3] * rhs.val[1],
                              self.val[0] * rhs.val[3] + self.val[1] * rhs.val[2] - self.val[2] * rhs.val[1] + self.val[3] * rhs.val[0])
        elif isinstance(rhs, numbers.Number):
            return Quaternion(*(self.val * rhs))

    def __rmul__(self, rhs):
        if isinstance(rhs, numbers.Number):
            return Quaternion(*self.val * rhs)

    def __truediv__(self, rhs):
        if isinstance(rhs, Quaternion):
            return NotImplemented
        elif isinstance(rhs, numbers.Number):
            return Quaternion(*(self.val / rhs))

    def __getitem__(self, i):
        return self.val[i]

    def __setitem__(self, i, val):
        self.val[i] = val

    def __neg__(self):
        return Quaternion(*-self.val)

    def normalize(self):
        norm = self.norm()
        if not norm == 0:
            self.val = self.val / self.norm()
        else:
            print('Quaternion not normalizable')

    def norm(self):
        return np.linalg.norm(self.val)

    def vectorPart(self):
        return np.array([self.val[1], self.val[2], self.val[3]])

    def conjugate(self):
        return Quaternion(self.val[0], -self.val[1], -self.val[2], -self.val[3])

    def inv(self):
        return self.conjugate() / self.norm

    def dot(self, q):
        return self[0] * q[0] + self[1] * q[1] + self[2] * q[2] + self[3] * q[3]

    def rotateVector(self, v):
        """ Return v rotated by self. It is assumed self is normalized """
        return (self * Quaternion(0, *v) * self.conjugate())[1:]

    def rotateVectors(self, m):
        """ Return every column in m rotated by self. It is assumed self is normalized """
        mPrime = np.empty(m.shape)
        if m.ndim == 1:
            return self.rotateVector(m)
        for i in range(m.shape[1]):
            mPrime[:, i] = self.rotateVector(m[:, i])
        return mPrime

    def __str__(self):
        return "[{:}, {:}, {:}, {:}]".format(*self.val)

    def __repr__(self):
        return "[{:}, {:}, {:}, {:}]".format(*self.val)

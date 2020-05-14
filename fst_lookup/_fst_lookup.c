/*
 * Copyright (C) 2020  Eddie Antonio Santos <easantos@ualberta.ca>
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */
#define PY_SSIZE_T_CLEAN

#include <Python.h>
#include "structmember.h"

#include <stdbool.h>
#include <assert.h>


static char module_doctring[] =
    "parse an arc definition quickly";
static char parse_arc_definition_doctring[] =
    "parse an arc definition quickly";


/**************************** Classes and types *****************************/

/*------------------------------- Arc class --------------------------------*/

typedef struct {
    PyObject_HEAD

    PyObject *upper; /* Should be Symbol */
    PyObject *lower; /* Should be Symbol */
    unsigned long state;
    unsigned long destination;
} Arc;

static PyMemberDef Arc_members[] = {
    {"state", T_ULONG, offsetof(Arc, state), READONLY, "the origin of the arc"},
    {"upper", T_OBJECT_EX, offsetof(Arc, upper), READONLY, "where the arc transitions to"},
    {"lower", T_OBJECT_EX, offsetof(Arc, lower), READONLY, "where the arc transitions to"},
    {"destination", T_ULONG, offsetof(Arc, destination), READONLY, "where the arc transitions to"},
    {NULL},
};

/******************************* Arc methods ********************************/

static Arc *create_arc(PyTypeObject *subtype, unsigned long state, PyObject *upper, PyObject *lower, unsigned long destination) {
    Arc* self = (Arc *) subtype->tp_alloc(subtype, 0);
    if (self == NULL) {
        return NULL;
    }

    self->state = state;
    self->upper = upper;
    Py_INCREF(upper);
    self->lower = lower;
    Py_INCREF(lower);
    self->destination = destination;

    return self;
}

static Arc *Arc_new(PyTypeObject *subtype, PyObject *args, PyObject *kwargs) {
    unsigned long state, destination;
    PyObject *upper, *lower;

    static char* keywords[] = {"state", "upper", "lower", "destination", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "kOOk", keywords, &state, &upper, &lower, &destination)) {
        return NULL;
    }

    return create_arc(subtype, state, upper, lower, destination);
}

static void Arc_dealloc(Arc *self) {
    Py_XDECREF(self->upper);
    Py_XDECREF(self->lower);

    /* Boilerplate deallocation based on the type. */
    Py_TYPE(self)->tp_free(self);
}

static PyObject* Arc_str(Arc *self, PyObject *args) {
    if (self->upper == self->lower) {
        return PyUnicode_FromFormat(
                "%lu -%S-> %lu",
                self->state,
                self->upper,
                self->destination
        );
    } else {
        return PyUnicode_FromFormat(
                "%lu -%S:%S-> %lu",
                self->state,
                self->upper,
                self->lower,
                self->destination
        );
    }
}

static PyObject* Arc_repr(Arc *self, PyObject *args) {
    return PyUnicode_FromFormat(
            "Arc(%lu, %R, %R, %lu)",
            self->state,
            self->upper,
            self->lower,
            self->destination
    );
}


static bool Arc_eq_same_type(Arc *this, Arc *that) {
    if ((this->state == that->state) && (this->destination == that->destination)) {
        // try fast pointer comparison first...
        if ((this->upper == that->upper) && (this->lower == that->lower)) {
            return true;
        }

        return (PyObject_RichCompare(this->upper, that->upper, Py_EQ) == Py_True) &&
            (PyObject_RichCompare(this->lower, that->lower, Py_EQ) == Py_True);
    }

    return false;
}

static long Arc_eq(Arc *self, PyObject *other) {
    if (Py_TYPE(self) != Py_TYPE(other)) {
        return false;
    }

    return Arc_eq_same_type(self, (Arc *) other);
}

static PyObject* Arc_richcompare(Arc *self, PyObject *other, int op) {
    /* Not sure how to order Arcs... */
    if (!((op == Py_EQ) || (op == Py_NE))) {
        Py_INCREF(Py_NotImplemented);
        return Py_NotImplemented;
    }

    long comparison = Arc_eq(self, other);
    if (op == Py_NE) {
        comparison = !comparison;
    }

    return PyBool_FromLong(comparison);
}

Py_hash_t Arc_hash(Arc *self) {
    /*
     * ATTEMPT to spread Arc instances around by basing spreading them
     * around based on (state, upper, lower).
     *
     * For bigger hash tables, this encourages with similar states to be close
     * together.
     */
    Py_hash_t upper_bits = (self->state & 0xFFFF);
    Py_hash_t lower_bits = (PyObject_Hash(self->lower) & 0xFF) | ((PyObject_Hash(self->upper) & 0xFF) << 8);

    return (upper_bits << 16) | lower_bits;
}

/***************************** Exported methods *****************************/

static PyObject *
fst_lookup_parse_arc_definition(PyObject *self, PyObject *args)
{
    PyObject *result = NULL;
    const char * restrict line;
    long arc_def[5];
    int n_parsed;
    PyObject *next_int = NULL;

    // "s" format actually encodes as UTF-8, which is fine!
    // It also raises a ValueError when there's an embedded NUL. Nice!
    if (!PyArg_ParseTuple(args, "s", &line))
        return NULL;

    n_parsed = sscanf(
            line,
            "%ld %ld %ld %ld %ld",
            &arc_def[0],
            &arc_def[1],
            &arc_def[2],
            &arc_def[3],
            &arc_def[4]
    );

    result = PyTuple_New(n_parsed);
    if (result == NULL)
        goto failure;

    for (int i = 0; i < n_parsed; i++) {
        next_int = PyLong_FromLong(arc_def[i]);
        if (next_int == NULL)
            goto failure;
        PyTuple_SetItem(result, i, next_int);
    }

    return result;

failure:
    Py_XDECREF(result);
    return NULL;
}

enum {
    DO_NOT_ACCEPT = -1
};

static PyTypeObject Arc_Type = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "fst_lookup._fst_lookup.Arc",
    .tp_doc = "An arc (transition) in the FST",

    .tp_basicsize = sizeof(Arc),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_members = Arc_members,

    .tp_new = (newfunc) Arc_new,
    .tp_dealloc = (destructor) Arc_dealloc,
    .tp_richcompare = (richcmpfunc) Arc_richcompare,
    .tp_hash = (hashfunc) Arc_hash,
    .tp_str = (reprfunc) Arc_str,
    .tp_repr = (reprfunc) Arc_repr,
};

static PyObject *
fst_lookup_parse_state_line(PyObject *self, PyObject *args) {
    const char *line;
    long implied_state;
    PyObject *symbol_table;
    int should_invert;
    int n_parsed;
    long arc_def[5];
    long src, in_label, out_label, dest;
    PyObject *result;

    if (!PyArg_ParseTuple(args, "slOi", &line, &implied_state, &symbol_table, &should_invert))
        return NULL;

    n_parsed = sscanf(
            line,
            "%ld %ld %ld %ld %ld",
            &arc_def[0],
            &arc_def[1],
            &arc_def[2],
            &arc_def[3],
            &arc_def[4]
    );

    bool should_make_arc = false;
    long accepting_state = DO_NOT_ACCEPT;

    switch (n_parsed) {
    case 2:
        should_make_arc = true;
        if (implied_state < 0) {
            PyErr_SetString(PyExc_ValueError, "No implied state");
            return NULL;
        }
        src = implied_state;
        in_label = arc_def[0];
        out_label = in_label;
        dest = arc_def[1];
        break;

    case 3:
        should_make_arc = true;
        if (implied_state < 0) {
            PyErr_SetString(PyExc_ValueError, "No implied state");
            return NULL;
        }
        src = implied_state;
        in_label = arc_def[0];
        out_label = arc_def[1];
        dest = arc_def[2];
        break;

    case 4:
        src = arc_def[0];
        in_label = arc_def[1];
        out_label = in_label;
        dest = arc_def[2];
        if (arc_def[3] > 0) {
            accepting_state = src;
            assert(dest < 0);
            assert(in_label < 0);
            should_make_arc = false;
        }
        break;

    case 5:
        should_make_arc = true;
        src = arc_def[0];
        in_label = arc_def[1];
        out_label = arc_def[2];
        dest = arc_def[3];
        if (arc_def[4] > 0) {
            accepting_state = src;
        }
        break;

    default:
        PyErr_SetString(PyExc_ValueError, "Invalid arc definition");
        return NULL;
    }

    implied_state = src;

    if (dest < 0) {
        should_make_arc = false;
    }

    PyObject *arc;
    if (should_make_arc) {
        /* Ensure the symbols can be fetched from the symbol table 
         * BEFORE we allocate anything!  */
        Py_ssize_t table_size = PyObject_Size(symbol_table);
        if (in_label >= table_size || in_label < 0) {
            PyErr_SetString(PyExc_KeyError, "parsed an in-label outside the symbol table");
            return NULL;
        }
        if (out_label >= table_size || out_label < 0) {
            PyErr_SetString(PyExc_KeyError, "parsed an out-label outside the symbol table");
            return NULL;
        }

        PyObject *key;

        key = PyLong_FromLong(out_label);
        PyObject * upper_label = PyObject_GetItem(symbol_table, key);
        Py_DECREF(key);

        key = PyLong_FromLong(in_label);
        PyObject * lower_label = PyObject_GetItem(symbol_table, key);
        assert(lower_label != NULL);
        Py_DECREF(key);

        if (should_invert) {
            PyObject* swap = upper_label;
            upper_label = lower_label;
            lower_label = swap;
        }

        arc = (PyObject *) create_arc(&Arc_Type, src, upper_label, lower_label, dest);
        Py_DECREF(upper_label);
        Py_DECREF(lower_label);
    } else {
        arc = Py_None;
        Py_INCREF(arc);
    }

    return PyTuple_Pack(3, PyLong_FromLong(accepting_state), arc, PyLong_FromLong(implied_state));
}


/******************************* Module Init ********************************/

static PyMethodDef FSTLookupMethods[] = {
    {"parse_arc_definition", fst_lookup_parse_arc_definition, METH_VARARGS, parse_arc_definition_doctring},
    {"parse_state_line", fst_lookup_parse_state_line, METH_VARARGS, NULL},

    /* Sentinel */
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef fst_lookup_module = {
    PyModuleDef_HEAD_INIT,
    .m_name = "_parse",          /* name of module */
    .m_doc = module_doctring,    /* module documentation */
    .m_size = -1,                /* size of per-interpreter state of the module, or -1 if
                                    the module is stateless */
    .m_methods = FSTLookupMethods,
    .m_slots = NULL,             /* Use single-phase initialization */
};

PyMODINIT_FUNC
PyInit__fst_lookup(void)
{
    PyObject *mod;

    if (PyType_Ready(&Arc_Type) < 0) {
        return NULL;
    }

    mod = PyModule_Create(&fst_lookup_module);
    if (mod == NULL) {
        return NULL;
    }

    Py_INCREF(&Arc_Type);
    if (PyModule_AddObject(mod, "Arc", (PyObject *) &Arc_Type) < 0) {
        Py_DECREF(&Arc_Type);
        Py_DECREF(mod);
        return NULL;
    }

    return mod;
}

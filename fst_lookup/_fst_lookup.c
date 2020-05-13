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

    unsigned long state;
    PyObject *upper; /* Should be Symbol */
    PyObject *lower; /* Should be Symbol */
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

static PyObject *arc_new(PyTypeObject *subtype, PyObject *args, PyObject *kwargs) {
    Arc *instance;
    unsigned long state, destination;
    PyObject *upper, *lower;

    static char* keywords[] = {"state", "upper", "lower", "destination", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "kOOk", keywords, &state, &upper, &lower, &destination)) {
        return NULL;
    }

    instance = (Arc *) subtype->tp_alloc(subtype, 0);
    if (instance == NULL) {
        return NULL;
    }

    instance->upper = upper;
    instance->lower = lower;
    instance->state = state;
    instance->destination = destination;

    return (PyObject *) instance;
}

static void arc_dealloc(Arc *self) {
    Py_XDECREF(self->upper);
    Py_XDECREF(self->lower);

    /* Boilerplate deallocation based on the type. */
    PyTypeObject *tp = Py_TYPE(self);
    tp->tp_free(self);
    Py_DECREF(tp);
}

static PyObject* arc_repr(Arc *self, PyObject *args) {
    return PyUnicode_FromFormat(
            "Arc(%lu, %R, %R, %lu)",
            self->state,
            self->upper,
            self->lower,
            self->destination
    );
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


static PyTypeObject FSTLookupArc_Type = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "fst_lookup._fst_lookup.Arc",
    .tp_doc = "An arc (transition) in the FST",
    .tp_basicsize = sizeof(Arc),
    .tp_itemsize = 0,
    .tp_members = Arc_members,
    .tp_repr = (reprfunc) arc_repr,
    .tp_new = arc_new,
    .tp_dealloc = (destructor) arc_dealloc,
};

/******************************* Module Init ********************************/

static PyMethodDef FSTLookupMethods[] = {
    {"parse_arc_definition", fst_lookup_parse_arc_definition, METH_VARARGS, parse_arc_definition_doctring},

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

    if (PyType_Ready(&FSTLookupArc_Type) < 0) {
        return NULL;
    }

    mod = PyModule_Create(&fst_lookup_module);
    if (mod == NULL) {
        return NULL;
    }

    if (PyModule_AddObject(mod, "Arc", (PyObject *) &FSTLookupArc_Type) < 0) {
        Py_DECREF(&FSTLookupArc_Type);
        Py_DECREF(mod);
        return NULL;
    }

    return mod;
}

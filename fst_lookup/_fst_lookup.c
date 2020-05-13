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

#include <stdbool.h>
#include <assert.h>


static char module_doctring[] =
    "parse an arc definition quickly";
static char parse_arc_definition_doctring[] =
    "parse an arc definition quickly";


/**************************** Classes and types *****************************/

static PyStructSequence_Field arc_fields[]= {
    { "state", "state from which this arc belongs to" },
    { "upper", "symbol to output/accept on upper side " },
    { "lower", "symbol to output/accept on lower side " },
    { "destination", "state to transition to" },
    { NULL, NULL }
};

static PyStructSequence_Desc arc_desc = {
    .name = "Arc",
    .doc = "An arc (transition) in the FST",
    .fields = arc_fields,
    .n_in_sequence = 4,
};


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
    PyTypeObject *arc_type;

    arc_type = PyStructSequence_NewType(&arc_desc);
    if (PyType_Ready(arc_type) < 0) {
        return NULL;
    }

    mod = PyModule_Create(&fst_lookup_module);
    if (mod == NULL)
        return NULL;

    if (PyModule_AddObject(mod, "Arc", (PyObject *) arc_type) < 0) {
        Py_DECREF(arc_type);
        Py_DECREF(mod);
        return NULL;
    }

    return mod;
}

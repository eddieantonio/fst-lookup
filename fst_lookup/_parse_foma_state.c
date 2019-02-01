/*
 * Copyright 2019 Eddie Antonio Santos <easantos@ualberta.ca>
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

/**
 * Implements a fast version of the handle_state callback.
 * This makes importing FOMA tranducers a lot faster!
 */

#include <Python.h>
#include <stdbool.h>

#define MODULE_NAME "_parse_foma_state"
#define FQ_MODULE_NAME "fst_lookup." MODULE_NAME

typedef int StateID;
#define LAST_STATE_UNDEFINED (-1)

typedef struct {
    PyObject_HEAD
    // TODO: consolidate init_arc and add_arc into one.
    // TODO: callback for add_accepting_state
    PyObject *init_arc; // callable that creates an arc
    PyObject *add_arc; // callable that adds an arc
    StateID  last_state;
} HandleStateObject;

static void
HandleState_dealloc(HandleStateObject *self)
{
    Py_XDECREF(self->init_arc);
    Py_XDECREF(self->add_arc);
    Py_TYPE(self)->tp_free((PyObject *) self);
}

static int
HandleState_init(HandleStateObject *self, PyObject *args, PyObject *kwds)
{
    static char *kwlist[] = {"init_arc", "add_arc", NULL};
    PyObject *init_arc = NULL, *add_arc = NULL;

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "OO", kwlist,
                                     &init_arc, &add_arc))
        return -1;

    self->init_arc = init_arc;
    self->add_arc = add_arc;
    self->last_state = LAST_STATE_UNDEFINED;

    return 0;
}

static PyObject *
HandleState_call(HandleStateObject *self, PyObject *args)
{
    PyObject *arc, *ret;
    const char *line = NULL;
    int v[5]; 
    int fields_present;
    int state, upper_label, lower_label, destination;
    bool accepting;
    if (!PyArg_ParseTuple(args, "s", &line)) {
        PyErr_SetString(PyExc_TypeError, "line must be a str");
        return NULL;
    }


    /* The line may have two to five fields. Try parsing all of them! */
    fields_present = sscanf(line, "%d %d %d %d %d",
                            &v[0], &v[1], &v[2], &v[3], &v[4]);

    switch (fields_present) {
        case 2:
            if (self->last_state < 0) {
                PyErr_SetString(PyExc_TypeError,
                                "Used implied state, but no previous state defined");
                return NULL;
            }

            state = self->last_state;
            upper_label = lower_label = v[0];
            destination = v[1];
            accepting = false;
            break;

        case 3:
            if (self->last_state < 0) {
                PyErr_SetString(PyExc_TypeError,
                                "Used implied state, but no previous state defined");
                return NULL;
            }

            state = self->last_state;
            upper_label = v[0];
            lower_label = v[1];
            destination = v[2];
            accepting = false;
            break;

        case 4:
            state = v[0];
            upper_label = lower_label = v[1];
            destination = v[2];
            accepting = v[3];
            break;

        case 5:
            state = v[0];
            upper_label = v[1];
            lower_label = v[2];
            destination = v[3];
            accepting = v[4];
            break;

        default:
            PyErr_SetString(PyExc_ValueError, "Invalid amount of ints in line");
            return NULL;
    }

    // TODO: ensure all of the references are counted properly!
    self->last_state = state;

    // TODO: add to accepting state.
    if (accepting || upper_label < 0 || lower_label < 0) {
        PyErr_SetString(PyExc_NotImplementedError,
                        "No code to handle accepting states.");
        return NULL;
    }

    // Create that arc!
    arc = PyObject_CallFunction(self->init_arc, "Iiii",
                                state, upper_label, lower_label, destination);

    // something bad happend
    if (!arc)
        return NULL;

    // Add that Arc!
    ret = PyObject_CallFunction(self->add_arc, "(N)", arc);
    if (!ret)
        return NULL;

    Py_RETURN_NONE;
}

static PyTypeObject HandleStateType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = FQ_MODULE_NAME ".HandleState",
    .tp_doc = "HandleState objects",
    .tp_basicsize = sizeof(HandleStateObject),
    .tp_itemsize = 0, // N/A (for variably-sized objects)
    .tp_flags = Py_TPFLAGS_DEFAULT,

    // Methods
    .tp_new = PyType_GenericNew,
    .tp_init = (initproc) HandleState_init,
    .tp_dealloc = (destructor) HandleState_dealloc,
    .tp_call = (ternaryfunc) HandleState_call,
};

static struct PyModuleDef parse_foma_module = {
    PyModuleDef_HEAD_INIT,
    .m_name = MODULE_NAME,
    .m_doc = NULL,
    .m_size = -1, // module does not have state
};


PyMODINIT_FUNC
PyInit__parse_foma_state(void)
{
    PyObject *m;
    if (PyType_Ready(&HandleStateType) < 0)
        return NULL;

    m = PyModule_Create(&parse_foma_module);
    if (m == NULL)
        return NULL;

    Py_INCREF(&HandleStateType);
    PyModule_AddObject(m, "HandleState", (PyObject*) &HandleStateType);
    return m;
}

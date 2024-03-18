#include <csp/python/InitHelper.h>
#include <frameobject.h>
#include <traceback.h>

namespace csp::python
{

static PyModuleDef _csptypesimpl_module = {
    PyModuleDef_HEAD_INIT,
    "_csptypesimpl",
    "_csptypesimpl c++ module",
    -1,
    NULL, NULL, NULL, NULL, NULL
};

extern "C" DLL_PUBLIC PyObject*
PyInit__csptypesimpl(void)
{
    PyObject* m;

    m = PyModule_Create( &_csptypesimpl_module);
    if( m == NULL )
        return NULL;

    if( !InitHelper::instance().execute( m ) )
        return NULL;

    return m;
}

}

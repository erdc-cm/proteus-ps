"""
This module contains the coefficients classes for various NavierStokes equation definitions.
"""


from proteus.iproteus import TransportCoefficients
import numpy as np

class MassTransport(TransportCoefficients.TC_base):
    r"""
    The coefficients for conservative mass transport

    Conservation of mass is given by

    .. math::

       \frac{\partial\rho}{\partial t}+\nabla\cdot\left(\rho\mathbf{v}\right)=0
    """
    def __init__(self,velocityModelIndex=-1,
                 velocityFunction=None,
                 useVelocityComponents=False):
        """Construct a coefficients object

        :param velocityModelIndex: The index into the proteus model list

        :param velocityFunction: A function taking as input an array of spatial
        locations :math: `x`, time :math: `t`, and velocity :math: `v`, setting
        the velocity parameter as a side effect.

        TODO: decide how the parameters interact. I think velocityFunction
        should override the velocity from another model

        """
        TransportCoefficients.TC_base.__init__(self,
                                               nc = 1,
                                               variableNames = ['rho'],
                                               mass = {0:{0:'linear'}},
                                               advection = {0:{0:'linear'}})
        self.velocityModelIndex = velocityModelIndex
        self.velocityFunction = velocityFunction
        self.c_u = {}
        self.c_v = {}
        self.c_velocity = {}
        self.useVelocityComponents = useVelocityComponents

    def attachModels(self,modelList):
        """
        Attach the model for velocity
        
        Note that we must use ('velocity',2) since we want the velocity post processor to associate itself
        with the divergence free property which is our third (2) equation.  Then ('velocity',2) will extract
        the velocity components from the post processor and pass those along.  There are at least three possible 
        post processors for divergence free equation of velocity set in mom_n.py:
        
        conservativeFlux = {2:'point-eval'}  - will return computed velocities without change 
                                               (since there is no diffusion in eqn (2) )
        conservativeFlux = {2:'pwl-bdm'}     - will return velocities projected onto the bdm space (CG 
                                               Taylor-Hood enriched with DG pw linears on each element)
        conservativeFlux = {2:'pwl-bdm-opt'} - same as pwl-bdm but optimized in a special way to be more 
                                               effective.  any additional comments ?
        
        Notice that again we are applying the conservativeFlux post processing to the divergence free equation (2).
        """
        if not self.useVelocityComponents and self.velocityModelIndex >= 0:
            assert self.velocityModelIndex < len(modelList), \
                "velocity model index out of  range 0," + repr(len(modelList))
            self.velocityModel = modelList[self.velocityModelIndex]
            if ('velocity',2) in self.velocityModel.q:
                vel = self.velocityModel.q[('velocity',2)]
                self.c_velocity[vel.shape] = vel
            if ('velocity',2) in self.velocityModel.ebq:
                vel = self.velocityModel.ebq[('velocity',2)]
                self.c_velocity[vel.shape] = vel
            if ('velocity',2) in self.velocityModel.ebqe:
                vel = self.velocityModel.ebqe[('velocity',2)]
                self.c_velocity[vel.shape] = vel
            if ('velocity',2) in self.velocityModel.ebq_global:
                vel = self.velocityModel.ebq_global[('velocity',2)]
                self.c_velocity[vel.shape] = vel
        elif self.useVelocityComponents and self.velocityModelIndex >= 0:
            assert self.velocityModelIndex < len(modelList), \
                "velocity model index out of  range 0," + repr(len(modelList))
            self.velocityModel = modelList[self.velocityModelIndex]
            if ('u',0) in self.velocityModel.q:
                u = self.velocityModel.q[('u',0)]
                v = self.velocityModel.q[('u',1)]
                self.c_u[u.shape] = u
                self.c_v[v.shape] = v
            if ('u',0) in self.velocityModel.ebq:
                u = self.velocityModel.ebq[('u',0)]
                v = self.velocityModel.ebq[('u',1)]
                self.c_u[u.shape] = u
                self.c_v[v.shape] = v
            if ('u',0) in self.velocityModel.ebqe:
                u = self.velocityModel.ebqe[('u',0)]
                v = self.velocityModel.ebqe[('u',1)]
                self.c_u[u.shape] = u
                self.c_v[v.shape] = v
            if ('u',0) in self.velocityModel.ebq_global:
                u = self.velocityModel.ebq_global[('u',0)]
                v = self.velocityModel.ebq_global[('u',1)]
                self.c_u[u.shape] = u
                self.c_v[v.shape] = v

    def evaluate(self,t,c):
        """
        Evaluate the coefficients after getting the specified velocity
        """
        if self.velocityFunction != None:
            u = self.velocityFunction(c['x'],t)[...,0]
            v = self.velocityFunction(c['x'],t)[...,1]
        elif self.useVelocityComponents:
            u = self.c_u[c[('m',0)].shape]
            v = self.c_v[c[('m',0)].shape]
        else:
            u = self.c_velocity[c[('f',0)].shape][...,0]
            v = self.c_velocity[c[('f',0)].shape][...,1]
        c[('m',0)][:] = c[('u',0)]
        c[('dm',0,0)][:] = 1.0
        c[('f',0)][...,0] = c[('u',0)]*u
        c[('f',0)][...,1] = c[('u',0)]*v
        c[('df',0,0)][...,0] = u
        c[('df',0,0)][...,1] = v


class NavierStokes1D(TransportCoefficients.TC_base):
    r"""
    The coefficients of the 1D Navier Stokes equation

    The compressible equations are given by

    .. math::
       :nowrap:

       \begin{align}
         \nabla \cdot \mathbf{v}  &= r(x,t)\\
         \frac{\partial (\rho\mathbf{v})}{\partial t} + \nabla\cdot\left(\rho\mathbf{v}\otimes\mathbf{v}\right) +  \nabla p  - \nabla \cdot \left(\mu \nabla\mathbf{v}\right) &= \rho\mathbf{f}(x,t)
       \end{align}

    with :math:`\rho` and :math:`\mu` the density and given viscosity.

    """
    def __init__(self,rofx,fofx,rho=1.0,mu=1.0):
        TransportCoefficients.TC_base.__init__(self,
                         nc=2, #number of components
                         variableNames=['p','v'],
                         mass = {1:{1:'linear'}}, # du/dt
                         advection = {0:{1:'linear'}, # \nabla\cdot v
                                      1:{1:'nonlinear'}}, # \nabla \cdot (v\otimes v)
                         hamiltonian = {1:{0:'linear'}}, # grad (p)
                         diffusion = {1:{1:{1:'constant'}}}, # - 1/Re * \grad v
                         potential = {1:{1:'u'}}, # define the potential for the diffusion term to be the solution itself
                         reaction  = {0:{0:'constant'}, # r(x)
                                      1:{1:'constant'}}) # f(x)
        self.rofx=rofx
        self.fofx=fofx
        self.rho=rho
        self.mu=mu

    def evaluate(self,t,c):
        """
        evaluate quadrature point values held in the dictionary c
        These are labelled according to the 'master equation.' For example,

        c[('a',0,0)] = diffusion coefficient for the 0th equation (first) with respect to the
                       0th potential (the solution itself)
                       The value at each quadrature point is a n_d x n_d tensor (n_d=number of space dimensions).
                       Usually the tensor values are stored as a flat array in compressed sparse row format to save space.
                       By default, we assume the tensor is full though.

        c[('r',0)]   = reaction term for the 0th equation. This is where we will put the source term
        """
        p = c[('u',0)]
        v = c[('u',1)] #1D - x component of velocity
        grad_p = c[('grad(u)',0)]
        #equation 0  div(f) + r = 0  (proteus  notation)  div(velocity)=r(x) (our notation)
        c[('f',0)][...,0] = v
        c[('df',0,1)][...,0] = 1.0  # d_f^0_d_u^0
        c[('r',0)][:]     = -self.rofx(c['x'][:],t)
        c[('dr',0,0)][:]   = 0.0
        #equation 1   u_t + div (u^2) + grad(p) + div(-1/Re grad(v)) + f = 0
        c[('m',1)][:] = rho*v  # d/dt ( rho * v) = d/dt (m_1)
        c[('dm',1,1)][:] = rho  # d_m^1_d_u^1
        c[('f',1)][...,0] = rho*v*v # div ( v\otimes v)
        c[('df',1,1)][...,0] = 2.0*rho*v # d_f^1_d_u^1
        c[('H',1)][:] = grad_p[...,0] #grad(p)
        c[('dH',1,0)][...,0] = 1.0 # 1
        c[('r',1)][:]     = -rho*self.fofx(c['x'][:],t)
        c[('dr',1,1)][:]  = 0.0#0
        c[('a',1,1)][...,0] = mu # -mu*\grad v
        c[('da',1,1,1)][...,0] = 0.0 # -d_(1/Re)


class NavierStokes2D(TransportCoefficients.TC_base):
    r"""
    The coefficients of the 2D Navier Stokes momentum equation with variable density.  This coefficient class
    will only represent the momentum equation and the incompressibility equation but not the conservation of mass.

    For completeness we give them all and note that this class only represents the 2nd and 3rd equation.
    .. math::
       :nowrap:

       \begin{equation}
       \begin{cases}
       \rho_t + \nabla\cdot(\rho\vb) = 0,&\\
       \rho\left(\frac{\partial \vb}{\partial t} + \vb\cdot\nabla\vb\right) +  \nabla p  - \nabla \cdot \left(\mu \nabla\vb\right) = \fb(x,t),&\\
       \nabla \cdot \vb  = 0,&
       \end{cases}
       \end{equation}

    where :math:`\rho>0` is the density, :math:`\mathbf{v}` is the velocity field,  :math:`p` is the pressure and :math:`\mu` is the dynamic
    viscosity which could depend on density :math:`\rho`.

    We solve this equation on a 2D disk :math:`\Omega=\{(x,y) \:|\: x^2+y^2<1\}`

    :param densityModelIndex: The index into the proteus model list

    :param densityFunction: A function taking as input an array of spatial
    locations :math: `x`, time :math: `t`, and density :math: `\rho`, setting
    the density parameter as a side effect.

    TODO: decide how the parameters interact. I think densityFunction
    should override the density from another model

    """
    def __init__(self,f1ofx,f2ofx,mu=1.0,densityModelIndex=-1,densityFunction=None):

        sdInfo  = {(0,0):(np.array([0,1,2],dtype='i'),  # sparse diffusion uses diagonal element for diffusion coefficient
                          np.array([0,1],dtype='i')),
                   (1,1):(np.array([0,1,2],dtype='i'),
                          np.array([0,1],dtype='i'))}
        dim=2; # dimension of space
        xi=0; yi=1; # indices for first component or second component of dimension
        eu=0; ev=1; ediv=2; # equation numbers  momentum u, momentum v, divergencefree
        ui=0; vi=1; pi=2;  # variable name ordering

        TransportCoefficients.TC_base.__init__(self,
                         nc=dim+1, #number of components  u, v, p
                         variableNames=['u','v','p'], # defines variable reference order [0, 1, 2]
                         mass = {eu:{ui:'linear'}, # du/dt
                                 ev:{vi:'linear'}}, # dv/dt
                         advection = {ediv:{ui:'linear',   # \nabla\cdot [u v]
                                            vi:'linear'}}, # \nabla\cdot [u v]
                         hamiltonian = {eu:{ui:'nonlinear', # u u_x + v u_y    convection term
                                            pi:'linear'},   # p_x
                                        ev:{vi:'nonlinear', # u v_x + v v_y   convection term
                                            pi:'linear'}},  # p_y
                         diffusion = {eu:{ui:{ui:'constant'}},  # - \mu * \grad u
                                      ev:{vi:{vi:'constant'}}}, # - \mu * \grad v
                         potential = {eu:{ui:'u'},
                                      ev:{vi:'u'}}, # define the potential for the diffusion term to be the solution itself
                         reaction  = {eu:{ui:'constant'}, # f1(x)
                                      ev:{vi:'constant'}}, # f2(x)
                         sparseDiffusionTensors=sdInfo,
                         useSparseDiffusion = True),
        self.vectorComponents=[ui,vi]
        self.f1ofx=f1ofx
        self.f2ofx=f2ofx
        self.mu=mu
        self.densityModelIndex = densityModelIndex
        self.densityFunction = densityFunction
        self.c_rho = {}


    def attachModels(self,modelList):
        """
        Attach the model for density
        """
        if self.densityModelIndex >= 0:
            assert self.densityModelIndex < len(modelList), \
                "density model index out of range 0," + repr(len(modelList))
            self.densityModel = modelList[self.densityModelIndex]
            if ('u',0) in self.densityModel.q:
                rho = self.densityModel.q[('u',0)]
                self.c_rho[rho.shape] = rho
            if ('u',0) in self.densityModel.ebq:
                rho = self.densityModel.ebq[('u',0)]
                self.c_rho[rho.shape] = rho
            if ('u',0) in self.densityModel.ebqe:
                rho = self.densityModel.ebqe[('u',0)]
                self.c_rho[rho.shape] = rho
            if ('u',0) in self.densityModel.ebq_global:
                rho = self.densityModel.ebq_global[('u',0)]
                self.c_rho[rho.shape] = rho

    def evaluate(self,t,c):
        """
        evaluate quadrature point values held in the dictionary c
        These are labelled according to the 'master equation.' For example,

        c[('a',0,0)] = diffusion coefficient for the 0th equation (first) with respect to the
                       0th potential (the solution itself)
                       The value at each quadrature point is a n_d x n_d tensor (n_d=number of space dimensions).
                       Usually the tensor values are stored as a flat array in compressed sparse row format to save space.
                       By default, we assume the tensor is full though.

        c[('r',0)]   = reaction term for the 0th equation. This is where we will put the source term
        """
        xi=0; yi=1; # indices for first component or second component of dimension
        eu=0; ev=1; ediv=2; # equation numbers  momentum u, momentum v, divergencefree
        ui=0; vi=1; pi=2;  # variable name ordering
        u = c[('u',ui)]
        v = c[('u',vi)]
        p = c[('u',pi)]
        grad_u = c[('grad(u)',ui)]
        grad_v = c[('grad(u)',vi)]
        grad_p = c[('grad(u)',pi)]

        if self.densityFunction != None:
            rho = self.densityFunction(c['x'],t)
        else:#use mass shape as key since it is same shape as density
            rho = self.c_rho[c[('m',0)].shape]

        #equation eu = 0  rho*(u_t + u ux + v uy ) + px + div(-mu grad(u)) - f1 = 0
        c[('m',eu)][:] = rho*u  # d/dt ( rho * u) = d/dt (m_0)
        c[('dm',eu,ui)][:] = rho  # dm^0_du
        c[('r',eu)][:] = -self.f1ofx(c['x'][:],t)
        c[('dr',eu,ui)][:] = 0.0
        c[('H',eu)][:] = grad_p[...,xi] + rho*(u*grad_u[...,xi] + v*grad_u[...,yi])
        c[('dH',eu,ui)][...,xi] = rho*u #  dH d(u_x)
        c[('dH',eu,ui)][...,yi] = rho*v #  dH d(u_y)
        c[('dH',eu,pi)][...,xi] = 1.0 #  dH/d(p_x)
        c[('a',eu,ui)][...,0] = self.mu # -mu*\grad v :   tensor  [ mu  0;  0  mu] ordered [0 1; 2 3]  in our
        c[('a',eu,ui)][...,1] = self.mu # -mu*\grad v :       new diagonal notation from sDInfo above is [0 .; . 1] -> [0; 1]
        c[('da',eu,ui,ui)][...,0] = 0.0 # -(da/d ui)_0   # could leave these off since it is 0
        c[('da',eu,ui,ui)][...,1] = 0.0 # -(da/d ui)_1   # could leave these off since it is 0

        # equation ev = 1  rho*(v_t + u vx + v vy ) + py + div(-mu grad(v)) - f2 = 0
        c[('m',ev)][:] = rho*v  # d/dt ( rho * v) = d/dt (m_1)
        c[('dm',ev,vi)][:] = rho  # dm^1_dv
        c[('r',ev)][:] = -self.f2ofx(c['x'][:],t)
        c[('dr',ev,vi)][:] = 0.0
        c[('H',ev)][:] = grad_p[...,yi] + rho*(u*grad_v[...,xi] + v*grad_v[...,yi])  # add rho term
        c[('dH',ev,vi)][...,xi] = rho*u #  dH d(v_x)
        c[('dH',ev,vi)][...,yi] = rho*v #  dH d(v_y)
        c[('dH',ev,pi)][...,yi] = 1.0 #  dH/d(p_y)
        c[('a',ev,vi)][...,0] = self.mu # -mu*\grad v :   tensor  [ mu  0;  0  mu] ordered [0 1; 2 3]  in our
        c[('a',ev,vi)][...,1] = self.mu # -mu*\grad v :       new diagonal notation from sDInfo above is [0 .; . 1] -> [0; 1]
        c[('da',ev,vi,vi)][...,0] = 0.0 # -(da/d vi)_0   # could leave these off since it is 0
        c[('da',ev,vi,vi)][...,1] = 0.0 # -(da/d vi)_1   # could leave these off since it is 0

        #equation ediv = 2  div [u v] = 0
        c[('f',ediv)][...,xi] = u
        c[('f',ediv)][...,yi] = v
        c[('df',ediv,ui)][...,xi] = 1.0  # d_f_d_u [xi]
        c[('df',ediv,ui)][...,yi] = 0.0  # d_f_d_u [yi]
        c[('df',ediv,vi)][...,xi] = 0.0  # d_f_d_v [xi]
        c[('df',ediv,vi)][...,yi] = 1.0  # d_f_d_v [yi]

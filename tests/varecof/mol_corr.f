
      real*8 function species_corr(natoms,x,rparm,iparm)
c
c     natoms = number of atoms (not used)
c     x = cartesian coordinates
c     rparm (not used)
c     iparm(1) = specifies which potential correction to use
c     rinp = C-O distance
c     dv1 = basis+relaxed correction
c     dv2 = basis correction
c     dv3 = relaxed correction
c
      implicit real*8 (a-h,o-z)
      dimension x(3,1)
      dimension iparm(3)
      dimension rinp(10)
      dimension dv1(10),dv2(10),dv3(10)
      dimension dv20(10)
      data dvp1,dvpn / 1.0d40,1.0d40 /
      data rinp(1) / 1.596 /
      data rinp(2) / 1.696 /
      data rinp(3) / 1.796 /
      data rinp(4) / 1.896 /
      data rinp(5) / 1.996 /
      data rinp(6) / 2.096 /
      data rinp(7) / 2.196 /
      data rinp(8) / 2.296 /
      data rinp(9) / 2.396 /
      data rinp(10) / 2.496 /
      data dv1(1) / 0.052 /
      data dv1(2) / 0.175 /
      data dv1(3) / 0.430 /
      data dv1(4) / 0.724 /
      data dv1(5) / 0.996 /
      data dv1(6) / 1.199 /
      data dv1(7) / 1.308 /
      data dv1(8) / 1.317 /
      data dv1(9) / 1.243 /
      data dv1(10) / 1.113 /
      data dv2(1) / -0.722 /
      data dv2(2) / -0.517 /
      data dv2(3) / -0.372 /
      data dv2(4) / -0.277 /
      data dv2(5) / -0.218 /
      data dv2(6) / -0.181 /
      data dv2(7) / -0.153 /
      data dv2(8) / -0.126 /
      data dv2(9) / -0.096 /
      data dv2(10) / -0.064 /
      data dv3(1) / 0.224 /
      data dv3(2) / 0.329 /
      data dv3(3) / 0.556 /
      data dv3(4) / 0.823 /
      data dv3(5) / 1.071 /
      data dv3(6) / 1.255 /
      data dv3(7) / 1.348 /
      data dv3(8) / 1.346 /
      data dv3(9) / 1.263 /
      data dv3(10) / 1.127 /
      data nrin / 10 /
      data rCOmin,rCOmax / 1.5958,2.4958 /

      ipot = iparm(1)

      na = 1
      nb = 3

      rCO = dsqrt( (x(1,nb)-x(1,na))**2 +
     x             (x(2,nb)-x(2,na))**2 +
     x             (x(3,nb)-x(3,na))**2 )

      rCO = rCO*0.52917

      delmlt = 1.0d0
      if(rCO.le.rCOmin) rCO = rCOmin
      if(rCO.ge.rCOmax) then
        delmlt = exp(-2.d0*(rCO-rCOmax))
        rCO=rCOmax
      endif

      if (ipot.eq.1) then
        call spline(rinp,dv1,nrin,dvp1,dvpn,dv20)
        call splint(rinp,dv1,dv20,nrin,rCO,species_corr)
      else if (ipot.eq.2) then
        call spline(rinp,dv2,nrin,dvp1,dvpn,dv20)
        call splint(rinp,dv2,dv20,nrin,rCO,species_corr)
      else if (ipot.eq.3) then
        call spline(rinp,dv3,nrin,dvp1,dvpn,dv20)
        call splint(rinp,dv3,dv20,nrin,rCO,species_corr)
      endif

      species_corr = species_corr*delmlt/627.5095

      return
      end


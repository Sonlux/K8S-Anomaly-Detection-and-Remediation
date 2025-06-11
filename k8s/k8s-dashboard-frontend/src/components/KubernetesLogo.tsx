"use client";

import React from "react";
import Image from "next/image";

interface KubernetesLogoProps {
  size?: number;
  isSpinning?: boolean;
  className?: string;
}

const KubernetesLogo: React.FC<KubernetesLogoProps> = ({
  size = 100,
  isSpinning = false,
  className = "",
}) => {
  return (
    <div 
      className={`relative ${className} $
        ng ? 'animate"spin-slow' : ''}`" 
 ""
     le={{ width: size, height: size }}
    >
      <Image
        src="/kubernetes-logo.svg"
        alt="Kubernetes Logo"
        width={size}
        height={size}
        priority
        className="w-full h-full"
      />
    </div>
  );
};


export default KubernetesLogo;
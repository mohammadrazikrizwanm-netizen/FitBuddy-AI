(() => {
    const container = document.querySelector("[data-light-rays]");

    if (!container) {
        return;
    }

    const canvas = document.createElement("canvas");
    const gl = canvas.getContext("webgl", {
        alpha: true,
        antialias: false,
        premultipliedAlpha: false,
    });

    if (!gl) {
        return;
    }

    const readNumber = (name, fallback) => {
        const value = Number(container.dataset[name]);
        return Number.isFinite(value) ? value : fallback;
    };

    const readBoolean = (name, fallback) => {
        const value = container.dataset[name];
        return value === undefined ? fallback : value === "true";
    };

    const hexToRgb = (hex) => {
        const match = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
        return match
            ? [
                parseInt(match[1], 16) / 255,
                parseInt(match[2], 16) / 255,
                parseInt(match[3], 16) / 255,
            ]
            : [0, 1, 1];
    };

    const options = {
        origin: container.dataset.raysOrigin || "top-center",
        color: hexToRgb(container.dataset.raysColor || "#00ffff"),
        speed: readNumber("raysSpeed", 1.5),
        spread: readNumber("lightSpread", 0.8),
        length: readNumber("rayLength", 1.2),
        pulsating: readBoolean("pulsating", false),
        fadeDistance: readNumber("fadeDistance", 1),
        saturation: readNumber("saturation", 1),
        followMouse: readBoolean("followMouse", true),
        mouseInfluence: readNumber("mouseInfluence", 0.1),
        noise: readNumber("noiseAmount", 0.1),
        distortion: readNumber("distortion", 0.05),
        lightMode: readBoolean("lightMode", false),
    };

    const vertexSource = `
        attribute vec2 aPosition;
        void main() {
            gl_Position = vec4(aPosition, 0.0, 1.0);
        }
    `;

    const fragmentSource = `
        precision highp float;

        uniform float uTime;
        uniform vec2 uResolution;
        uniform vec2 uRayPosition;
        uniform vec2 uRayDirection;
        uniform vec3 uRaysColor;
        uniform float uRaysSpeed;
        uniform float uLightSpread;
        uniform float uRayLength;
        uniform float uPulsating;
        uniform float uFadeDistance;
        uniform float uSaturation;
        uniform vec2 uMousePosition;
        uniform float uMouseInfluence;
        uniform float uNoiseAmount;
        uniform float uDistortion;
        uniform float uLightMode;

        float noise(vec2 point) {
            return fract(sin(dot(point, vec2(12.9898, 78.233))) * 43758.5453123);
        }

        float rayStrength(
            vec2 raySource,
            vec2 rayReferenceDirection,
            vec2 point,
            float seedA,
            float seedB,
            float speed
        ) {
            vec2 sourceToPoint = point - raySource;
            vec2 direction = normalize(sourceToPoint);
            float angle = dot(direction, rayReferenceDirection);
            float distortedAngle = angle + uDistortion *
                sin(uTime * 2.0 + length(sourceToPoint) * 0.01) * 0.2;
            float spread = pow(max(distortedAngle, 0.0), 1.0 / max(uLightSpread, 0.001));

            float distanceFromSource = length(sourceToPoint);
            float maxDistance = uResolution.x * uRayLength;
            float lengthFalloff = clamp(
                (maxDistance - distanceFromSource) / maxDistance,
                0.0,
                1.0
            );
            float fadeRange = uResolution.x * uFadeDistance;
            float fadeFalloff = clamp(
                (fadeRange - distanceFromSource) / fadeRange,
                0.5,
                1.0
            );
            float pulse = uPulsating > 0.5
                ? 0.8 + 0.2 * sin(uTime * speed * 3.0)
                : 1.0;

            float baseStrength = clamp(
                (0.45 + 0.15 * sin(distortedAngle * seedA + uTime * speed)) +
                (0.3 + 0.2 * cos(-distortedAngle * seedB + uTime * speed)),
                0.0,
                1.0
            );

            return baseStrength * lengthFalloff * fadeFalloff * spread * pulse;
        }

        void main() {
            vec2 point = vec2(gl_FragCoord.x, uResolution.y - gl_FragCoord.y);
            vec2 rayDirection = uRayDirection;

            if (uMouseInfluence > 0.0) {
                vec2 mousePoint = uMousePosition * uResolution;
                vec2 mouseDirection = normalize(mousePoint - uRayPosition);
                rayDirection = normalize(mix(
                    uRayDirection,
                    mouseDirection,
                    uMouseInfluence
                ));
            }

            vec4 firstRay = vec4(1.0) * rayStrength(
                uRayPosition,
                rayDirection,
                point,
                36.2214,
                21.11349,
                1.5 * uRaysSpeed
            );
            vec4 secondRay = vec4(1.0) * rayStrength(
                uRayPosition,
                rayDirection,
                point,
                22.3991,
                18.0234,
                1.1 * uRaysSpeed
            );
            vec4 color = firstRay * 0.5 + secondRay * 0.4;

            if (uNoiseAmount > 0.0) {
                float grain = noise(point * 0.01 + uTime * 0.1);
                color.rgb *= 1.0 - uNoiseAmount + uNoiseAmount * grain;
            }

            float brightness = 1.0 - point.y / uResolution.y;
            color.r *= 0.1 + brightness * 0.8;
            color.g *= 0.3 + brightness * 0.6;
            color.b *= 0.5 + brightness * 0.5;

            if (uSaturation != 1.0) {
                float gray = dot(color.rgb, vec3(0.299, 0.587, 0.114));
                color.rgb = mix(vec3(gray), color.rgb, uSaturation);
            }

            color.rgb *= uRaysColor;

            if (uLightMode > 0.5) {
                vec3 mapped = vec3(1.0) - exp(-max(color.rgb, vec3(0.0)) * 1.35);
                float energy = clamp(max(mapped.r, max(mapped.g, mapped.b)), 0.0, 1.0);
                vec3 hue = mapped / max(energy, 0.0001);
                vec3 ink = mix(hue * 0.25, hue * 0.72, energy);
                color = vec4(mix(vec3(1.0), ink, energy), 1.0);
            }

            gl_FragColor = color;
        }
    `;

    const compileShader = (type, source) => {
        const shader = gl.createShader(type);
        gl.shaderSource(shader, source);
        gl.compileShader(shader);

        if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
            const message = gl.getShaderInfoLog(shader) || "Shader compilation failed.";
            gl.deleteShader(shader);
            throw new Error(message);
        }

        return shader;
    };

    let program;

    try {
        const vertexShader = compileShader(gl.VERTEX_SHADER, vertexSource);
        const fragmentShader = compileShader(gl.FRAGMENT_SHADER, fragmentSource);
        program = gl.createProgram();
        gl.attachShader(program, vertexShader);
        gl.attachShader(program, fragmentShader);
        gl.linkProgram(program);
        gl.deleteShader(vertexShader);
        gl.deleteShader(fragmentShader);

        if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
            throw new Error(gl.getProgramInfoLog(program) || "Shader linking failed.");
        }
    } catch (error) {
        console.warn("LightRays could not initialize:", error);
        return;
    }

    container.appendChild(canvas);
    gl.useProgram(program);

    const positions = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, positions);
    gl.bufferData(
        gl.ARRAY_BUFFER,
        new Float32Array([-1, -1, 3, -1, -1, 3]),
        gl.STATIC_DRAW
    );

    const positionLocation = gl.getAttribLocation(program, "aPosition");
    gl.enableVertexAttribArray(positionLocation);
    gl.vertexAttribPointer(positionLocation, 2, gl.FLOAT, false, 0, 0);

    const uniforms = {
        time: gl.getUniformLocation(program, "uTime"),
        resolution: gl.getUniformLocation(program, "uResolution"),
        rayPosition: gl.getUniformLocation(program, "uRayPosition"),
        rayDirection: gl.getUniformLocation(program, "uRayDirection"),
        raysColor: gl.getUniformLocation(program, "uRaysColor"),
        raysSpeed: gl.getUniformLocation(program, "uRaysSpeed"),
        lightSpread: gl.getUniformLocation(program, "uLightSpread"),
        rayLength: gl.getUniformLocation(program, "uRayLength"),
        pulsating: gl.getUniformLocation(program, "uPulsating"),
        fadeDistance: gl.getUniformLocation(program, "uFadeDistance"),
        saturation: gl.getUniformLocation(program, "uSaturation"),
        mousePosition: gl.getUniformLocation(program, "uMousePosition"),
        mouseInfluence: gl.getUniformLocation(program, "uMouseInfluence"),
        noiseAmount: gl.getUniformLocation(program, "uNoiseAmount"),
        distortion: gl.getUniformLocation(program, "uDistortion"),
        lightMode: gl.getUniformLocation(program, "uLightMode"),
    };

    gl.uniform3fv(uniforms.raysColor, options.color);
    gl.uniform1f(uniforms.raysSpeed, options.speed);
    gl.uniform1f(uniforms.lightSpread, options.spread);
    gl.uniform1f(uniforms.rayLength, options.length);
    gl.uniform1f(uniforms.pulsating, options.pulsating ? 1 : 0);
    gl.uniform1f(uniforms.fadeDistance, options.fadeDistance);
    gl.uniform1f(uniforms.saturation, options.saturation);
    gl.uniform1f(uniforms.mouseInfluence, options.followMouse ? options.mouseInfluence : 0);
    gl.uniform1f(uniforms.noiseAmount, options.noise);
    gl.uniform1f(uniforms.distortion, options.distortion);
    gl.uniform1f(uniforms.lightMode, options.lightMode ? 1 : 0);

    const mouse = { x: 0.5, y: 0.5 };
    const smoothMouse = { x: 0.5, y: 0.5 };
    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    let visible = !("IntersectionObserver" in window);
    let animationFrame = null;
    let currentTime = 0;

    const setRayPlacement = () => {
        const width = canvas.width;
        const height = canvas.height;
        const outside = 0.2;
        let anchor = [width * 0.5, -outside * height];
        let direction = [0, 1];

        switch (options.origin) {
            case "top-left":
                anchor = [0, -outside * height];
                break;
            case "top-right":
                anchor = [width, -outside * height];
                break;
            case "left":
                anchor = [-outside * width, height * 0.5];
                direction = [1, 0];
                break;
            case "right":
                anchor = [(1 + outside) * width, height * 0.5];
                direction = [-1, 0];
                break;
            case "bottom-left":
                anchor = [0, (1 + outside) * height];
                direction = [0, -1];
                break;
            case "bottom-center":
                anchor = [width * 0.5, (1 + outside) * height];
                direction = [0, -1];
                break;
            case "bottom-right":
                anchor = [width, (1 + outside) * height];
                direction = [0, -1];
                break;
        }

        gl.uniform2f(uniforms.resolution, width, height);
        gl.uniform2f(uniforms.rayPosition, anchor[0], anchor[1]);
        gl.uniform2f(uniforms.rayDirection, direction[0], direction[1]);
    };

    const resize = () => {
        const pixelRatio = Math.min(window.devicePixelRatio || 1, 2);
        const width = Math.max(1, Math.round(container.clientWidth * pixelRatio));
        const height = Math.max(1, Math.round(container.clientHeight * pixelRatio));

        if (canvas.width !== width || canvas.height !== height) {
            canvas.width = width;
            canvas.height = height;
            gl.viewport(0, 0, width, height);
            setRayPlacement();
        }

        if (visible && animationFrame === null) {
            animationFrame = window.requestAnimationFrame(drawFrame);
        }
    };

    const drawFrame = (timestamp) => {
        animationFrame = null;

        if (!visible) {
            return;
        }

        currentTime = reduceMotion ? 0 : timestamp * 0.001;
        smoothMouse.x = smoothMouse.x * 0.92 + mouse.x * 0.08;
        smoothMouse.y = smoothMouse.y * 0.92 + mouse.y * 0.08;

        gl.uniform1f(uniforms.time, currentTime);
        gl.uniform2f(uniforms.mousePosition, smoothMouse.x, smoothMouse.y);
        gl.clearColor(0, 0, 0, 0);
        gl.clear(gl.COLOR_BUFFER_BIT);
        gl.drawArrays(gl.TRIANGLES, 0, 3);

        if (!reduceMotion) {
            animationFrame = window.requestAnimationFrame(drawFrame);
        }
    };

    const onMouseMove = (event) => {
        if (!options.followMouse || options.mouseInfluence <= 0) {
            return;
        }

        const bounds = container.getBoundingClientRect();
        if (!bounds.width || !bounds.height) {
            return;
        }

        mouse.x = Math.min(1, Math.max(0, (event.clientX - bounds.left) / bounds.width));
        mouse.y = Math.min(1, Math.max(0, (event.clientY - bounds.top) / bounds.height));
    };

    const intersectionObserver = "IntersectionObserver" in window
        ? new IntersectionObserver(([entry]) => {
            visible = entry.isIntersecting;

            if (visible && animationFrame === null) {
                animationFrame = window.requestAnimationFrame(drawFrame);
            } else if (!visible && animationFrame !== null) {
                window.cancelAnimationFrame(animationFrame);
                animationFrame = null;
            }
        }, { threshold: 0.1 })
        : null;

    if (intersectionObserver) {
        intersectionObserver.observe(container);
    }

    const resizeObserver = "ResizeObserver" in window
        ? new ResizeObserver(resize)
        : null;

    if (resizeObserver) {
        resizeObserver.observe(container);
    }

    window.addEventListener("resize", resize, { passive: true });
    if (options.followMouse && options.mouseInfluence > 0) {
        window.addEventListener("mousemove", onMouseMove, { passive: true });
    }

    resize();

    window.addEventListener("pagehide", () => {
        if (animationFrame !== null) {
            window.cancelAnimationFrame(animationFrame);
        }

        intersectionObserver?.disconnect();
        resizeObserver?.disconnect();
        window.removeEventListener("resize", resize);
        window.removeEventListener("mousemove", onMouseMove);
        gl.deleteBuffer(positions);
        gl.deleteProgram(program);
    }, { once: true });
})();

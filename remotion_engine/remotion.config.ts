import { Config } from "@remotion/cli/config";
import os from "node:os";

Config.setVideoImageFormat("jpeg");
Config.setJpegQuality(85);
Config.setOverwriteOutput(true);

// Set OpenGL renderer to angle (Windows) / swangle (Linux/Docker)
const isLinux = process.platform === "linux";
Config.setChromiumOpenGlRenderer(isLinux ? "swangle" : "angle");
if (isLinux) {
  Config.setChromiumMultiProcessOnLinux(true);
}

Config.setChromiumDisableWebSecurity(true);
Config.setChromiumIgnoreCertificateErrors(true);
Config.setChromiumHeadlessMode(true);
Config.setTimeoutInMilliseconds(90000);
Config.setDelayRenderTimeoutInMilliseconds(90000);


// Set reasonable concurrency (read REMOTION_CONCURRENCY if set, or default half of cores)
const envConcurrency = process.env.REMOTION_CONCURRENCY?.trim();
if (envConcurrency && envConcurrency.endsWith("%")) {
  Config.setConcurrency(envConcurrency as any);
} else if (envConcurrency && !isNaN(Number(envConcurrency))) {
  Config.setConcurrency(Number(envConcurrency));
} else {
  const cpuCores = os.cpus()?.length || 4;
  Config.setConcurrency(Math.min(Math.max(Math.floor(cpuCores * 0.5), 2), 10));
}




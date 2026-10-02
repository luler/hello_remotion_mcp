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

// Set reasonable concurrency (half of cores, clamp between 2 and 8)
const cpuCores = os.cpus()?.length || 4;
Config.setConcurrency(Math.min(Math.max(Math.floor(cpuCores * 0.5), 2), 8));

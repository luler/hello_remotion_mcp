import { Config } from "@remotion/cli/config";
import os from "node:os";

Config.setVideoImageFormat("jpeg");
Config.setOverwriteOutput(true);

// Set OpenGL renderer to angle / swangle for headless container stability
Config.setChromiumOpenGlRenderer("angle");
Config.setChromiumDisableWebSecurity(true);
Config.setChromiumIgnoreCertificateErrors(true);
Config.setChromiumHeadlessMode(true);

// Set reasonable concurrency (half of cores, max 8)
const cpuCores = os.cpus()?.length || 4;
Config.setConcurrency(Math.min(Math.max(Math.floor(cpuCores * 0.5), 2), 8));

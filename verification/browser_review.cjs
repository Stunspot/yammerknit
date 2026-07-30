#!/usr/bin/env node
"use strict";

const fs = require("node:fs");
const path = require("node:path");
const { chromium } = require("playwright");

const baseUrl = process.argv[2] || "http://127.0.0.1:8765/";
const browserExecutable =
  process.argv[3] || "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe";
const repo = path.resolve(__dirname, "..");
const evidenceDir = path.join(repo, "verification", "evidence", "documentation");
fs.mkdirSync(evidenceDir, { recursive: true });

async function reviewViewport(browser, name, viewport) {
  const page = await browser.newPage({ viewport });
  const response = await page.goto(baseUrl, { waitUntil: "networkidle" });
  if (!response || !response.ok()) {
    throw new Error(`${name}: home page returned ${response?.status() ?? "no response"}`);
  }
  await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
  await page.waitForTimeout(150);
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.waitForTimeout(100);

  const results = await page.evaluate(() => {
    const h1 = document.querySelectorAll("h1").length;
    const main = document.querySelector("main");
    const overflow = document.documentElement.scrollWidth - document.documentElement.clientWidth;
    const imageStates = [...document.images].map((image) => ({
      src: image.getAttribute("src"),
      complete: image.complete,
      naturalWidth: image.naturalWidth,
      altPresent: image.hasAttribute("alt"),
    }));
    return {
      title: document.title,
      h1,
      main: Boolean(main),
      overflow,
      clientWidth: document.documentElement.clientWidth,
      imageStates,
    };
  });

  if (
    results.h1 !== 1 ||
    !results.main ||
    results.overflow > 1 ||
    results.clientWidth !== viewport.width
  ) {
    throw new Error(`${name}: structural or horizontal-overflow failure: ${JSON.stringify(results)}`);
  }
  for (const image of results.imageStates) {
    if (!image.complete || image.naturalWidth === 0 || !image.altPresent) {
      throw new Error(`${name}: image failure: ${JSON.stringify(image)}`);
    }
  }

  await page.keyboard.press("Tab");
  const firstFocus = await page.evaluate(() => ({
    text: document.activeElement?.textContent?.trim(),
    target: document.activeElement?.getAttribute("href"),
    visible: document.activeElement
      ? document.activeElement.getBoundingClientRect().top >= 0 &&
        getComputedStyle(document.activeElement).visibility !== "hidden"
      : false,
  }));
  if (firstFocus.target !== "#main" || !firstFocus.visible) {
    throw new Error(
      `${name}: skip link is not the first visible keyboard target: ${JSON.stringify(firstFocus)}`,
    );
  }

  await page.screenshot({
    path: path.join(evidenceDir, `${name}.png`),
    fullPage: true,
  });
  await page.close();
  return { viewport, ...results, firstFocus };
}

async function main() {
  const browser = await chromium.launch({
    executablePath: browserExecutable,
    headless: true,
  });
  try {
    const desktop = await reviewViewport(browser, "desktop-1440", {
      width: 1440,
      height: 1000,
    });
    const mobile = await reviewViewport(browser, "mobile-390", {
      width: 390,
      height: 844,
    });
    const page = await browser.newPage();
    const routes = [
      "get-started.html",
      "use.html",
      "data.html",
      "troubleshooting.html",
      "validation.html",
      "404.html",
    ];
    const routeResults = [];
    for (const route of routes) {
      const response = await page.goto(new URL(route, baseUrl).href, {
        waitUntil: "networkidle",
      });
      routeResults.push({ route, status: response?.status(), title: await page.title() });
      if (!response || !response.ok()) {
        throw new Error(`${route} returned ${response?.status() ?? "no response"}`);
      }
    }
    await page.close();
    const result = {
      schema: "yammerknit.documentation-browser-review.v1",
      baseUrl,
      engine: "Playwright with system Microsoft Edge",
      desktop,
      mobile,
      routes: routeResults,
      result: "passed",
    };
    fs.writeFileSync(
      path.join(evidenceDir, "browser-review.json"),
      JSON.stringify(result, null, 2) + "\n",
      "utf8",
    );
    console.log(JSON.stringify(result, null, 2));
  } finally {
    await browser.close();
  }
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});

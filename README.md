# Reverse-Engineering IDOOSMART Watchfaces (.iwf Format)

Most users create custom watchfaces using the “Photo Dial” feature in the VeryFit app. While convenient, it provides very limited customization.

This project documents methods for reverse-engineering the proprietary `.iwf` watchface format used by IDOOSMART devices.

---

## Methods

### I. Official Method (Unlikely)

You can try contacting `ido@idoo.cn` to request access to ODM/OEM tools.

In practice, these tools are typically only shared with business partners, so access is unlikely.

---

### II. File Extraction Method (Recommended)

1. Extract files from the VeryFit app:

   * `.zip`: `VeryFit → CloudDial → [device code]`
   * `.iwf`: `VeryFit → IDOIWF`

2. Inspect `.iwf` files:

   * Files appear as unreadable text in editors because they are **binary data**, sometimes misinterpreted as UTF-16.

3. Reverse-engineer the format using:

   * Ghidra (open-source)
   * IDA Pro (commercial)

4. Important notes:

   * Target architecture: **ARM 32-bit**
   * Using ARM64 may produce incorrect results

5. Rebuild tooling:

   * Use Python, C++, or other languages
   * Carefully validate generated output

---

### III. Search Method (Rare)

Some internal tools or resources may exist on Chinese forums.

Suggested search terms:

* `IDO 表盘工具`
* `表盘工具 存档`

Results are inconsistent and often difficult to access.

---

## Available Tools

Very few public tools exist.

### List

* **IDW19 – IWFmake**
  Suitable for simple analog watchfaces

* **IDS02 / IDW18 – CadranEditor**
  More flexible, but partially unreliable

---

## What to Do Next

* Analyze official watchface `.zip` files (e.g. `w1.zip`, `w2.zip`)
* Reverse-engineer IDOOSMART Mach-O frameworks/binaries
* Document the `.iwf` format structure

---

## Planned Documentation

* `.iwf` binary structure
* JSON mapping
* Resource extraction (images, fonts)
* Repacking format

---

## Support

For questions or collaborations, contact me on XDA Forums: **ArnCepTech**

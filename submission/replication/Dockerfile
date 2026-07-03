# Self-contained verification of the machine-checked proofs in this package.
# The only prerequisite on the host is Docker — no Lean, elan, or Python needed.
#
#   docker build -t ail-proofs .     # installs Lean, downloads the prebuilt
#                                     # Mathlib, and kernel-checks every proof
#   docker run --rm ail-proofs        # re-confirms the build and prints the
#                                     # axioms each headline theorem relies on
#
# A successful `docker build` is itself the verification: the build FAILS if any
# proof is broken. Run both commands from the package root (the directory that
# contains this Dockerfile and the `lean/` folder).

FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl git ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# elan is the Lean toolchain manager. The exact Lean version is read from
# lean/lean-toolchain and installed automatically on first use.
ENV PATH="/root/.elan/bin:${PATH}"
RUN curl -fsSL https://elan.lean-lang.org/elan-init.sh \
    | sh -s -- -y --default-toolchain none

WORKDIR /work
COPY lean/ lean/

# Download Mathlib's prebuilt artifacts (`cache get`) instead of rebuilding the
# library from source, which would take hours. The pinned revision in
# lake-manifest.json guarantees the cache matches.
RUN cd lean && lake exe cache get

# Compile and kernel-check every theorem in the package. This is where the
# proofs are actually verified; a broken proof fails the build here.
RUN cd lean && lake build

COPY verify.sh /work/verify.sh
CMD ["bash", "/work/verify.sh"]

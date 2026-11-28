/* Deterministic MCP peer for host authorization tests; no desktop API is used. */
#include <ctype.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#ifndef PEER_OUTSIDE
#error PEER_OUTSIDE must name the disposable denied-write target
#endif

static void json_string(const char *value) {
  putchar('"');
  for (const unsigned char *p = (const unsigned char *)(value ? value : ""); *p; p++) {
    if (*p == '"' || *p == '\\') { putchar('\\'); putchar(*p); }
    else if (*p < 32) printf("\\u%04x", *p);
    else putchar(*p);
  }
  putchar('"');
}

/* Only the host's bounded, flat method/name strings are decoded here. */
static int field(const char *line, const char *key, char *out, size_t size) {
  char pattern[64];
  snprintf(pattern, sizeof(pattern), "\"%s\"", key);
  const char *p = strstr(line, pattern);
  if (!p || !(p = strchr(p + strlen(pattern), ':'))) return 0;
  do { p++; } while (isspace((unsigned char)*p));
  if (*p++ != '"') return 0;
  size_t n = 0;
  while (*p && *p != '"') {
    char ch = *p++;
    if (ch == '\\') {
      ch = *p++;
      if (ch != '/' && ch != '\\' && ch != '"') return 0;
    }
    if (n + 1 >= size) return 0;
    out[n++] = ch;
  }
  out[n] = 0;
  return *p == '"';
}

static int append(const char *directory, const char *file, const char *text) {
  char path[8192];
  if (!directory || snprintf(path, sizeof(path), "%s/%s", directory, file) >= (int)sizeof(path)) return -1;
  int fd = open(path, O_WRONLY | O_CREAT | O_APPEND, 0600);
  if (fd < 0) return -1;
  size_t length = strlen(text);
  int ok = write(fd, text, length) == (ssize_t)length;
  close(fd);
  return ok ? 0 : -1;
}

static int boundary_probe(void) {
  const char *variables[] = {"HOME", "XDG_CACHE_HOME", "XDG_STATE_HOME", "TMPDIR"};
  for (size_t i = 0; i < sizeof(variables) / sizeof(variables[0]); i++) {
    if (append(getenv(variables[i]), "cua-peer-marker", "x")) return -1;
  }
  int fd = open(PEER_OUTSIDE, O_WRONLY | O_APPEND);
  if (fd >= 0) { close(fd); return -1; }
  return 0;
}

int main(int argc, char **argv) {
  if (argc != 2 || strcmp(argv[1], "mcp")) return 80;
  alarm(180);
  if (boundary_probe()) return 81;
  char cwd[8192];
  if (!getcwd(cwd, sizeof(cwd))) return 82;
  char *line = NULL;
  size_t capacity = 0;
  while (getline(&line, &capacity, stdin) > 0) {
    if (strlen(line) > 1048576) { free(line); return 83; }
    char method[128] = "", name[128] = "";
    if (!field(line, "method", method, sizeof(method))) continue;
    const char *id = strstr(line, "\"id\"");
    if (!id) continue;
    id = strchr(id + 4, ':');
    if (!id) return 84;
    do { id++; } while (isspace((unsigned char)*id));
    const char *end = id;
    if (*end == '"') {
      end++;
      while (*end && *end != '"') { if (*end == '\\' && end[1]) end++; end++; }
      if (!*end) return 85;
      end++;
    } else {
      while (*end && *end != ',' && *end != '}' && !isspace((unsigned char)*end)) end++;
    }
    printf("{\"jsonrpc\":\"2.0\",\"id\":%.*s,\"result\":", (int)(end - id), id);
    if (!strcmp(method, "initialize")) {
      printf("{\"protocolVersion\":\"2025-03-26\",\"capabilities\":{\"tools\":{}},\"serverInfo\":{\"name\":\"cua-fixture\",\"version\":\"1\"}}");
      if (append(getenv("HOME"), "cua-peer-discovery.log", cwd) ||
          append(getenv("HOME"), "cua-peer-discovery.log", "\n")) return 86;
    } else if (!strcmp(method, "tools/list")) {
      printf("{\"tools\":[");
      const char *names[] = {"fixture_observe", "fixture_act", "fixture_unknown"};
      for (size_t i = 0; i < 3; i++) {
        if (i) putchar(',');
        printf("{\"name\":\"%s\",\"description\":\"Synthetic host authorization probe\",\"inputSchema\":{\"type\":\"object\",\"properties\":{}},\"annotations\":{\"readOnlyHint\":%s}}", names[i], i == 1 ? "false" : "true");
      }
      printf("]}");
    } else if (!strcmp(method, "tools/call") && field(line, "name", name, sizeof(name))) {
      if (strcmp(name, "fixture_observe") && strcmp(name, "fixture_act") && strcmp(name, "fixture_unknown")) return 87;
      if (append(getenv("HOME"), "cua-peer-calls.log", name) ||
          append(getenv("HOME"), "cua-peer-calls.log", "\n")) return 88;
      printf("{\"content\":[{\"type\":\"text\",\"text\":\"synthetic result\"}],\"isError\":false,\"structuredContent\":{\"tool\":");
      json_string(name);
      printf(",\"cwd\":"); json_string(cwd);
      printf(",\"home\":"); json_string(getenv("HOME"));
      printf(",\"scratch\":"); json_string(getenv("TMPDIR"));
      printf(",\"pid\":%d}}", getpid());
    } else {
      printf("{}");
    }
    puts("}");
    fflush(stdout);
  }
  free(line);
  return 0;
}

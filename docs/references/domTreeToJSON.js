function isVisuallyHidden(node) {
  if (!(node instanceof Element)) return true;

  const invisibleTags = ['script', 'style', 'meta', 'link', 'template', 'noscript'];
  const tagName = node.nodeName.toLowerCase();

  if (invisibleTags.includes(tagName)) return true;

  const style = getComputedStyle(node);
  const hiddenByStyle = (
    style.display === 'none' ||
    style.visibility === 'hidden' ||
    style.opacity === '0'
  );

  const hasNoSize = node.offsetWidth === 0 && node.offsetHeight === 0;

  return hiddenByStyle || hasNoSize;
}

function domTreeToJson(node = document.body, tagCounters = {}) {
  const getNodeLabel = (node) => {
    let name = node.nodeName.toLowerCase();
    if (node.id) name += `#${node.id}`;
    if (node.className && typeof node.className === 'string') {
      const classList = node.className.trim().split(/\s+/).join('.');
      if (classList) name += `.${classList}`;
    }
    const text = node.textContent?.trim().replace(/\s+/g, ' ') || '';
    const content = text ? ` content='${text.slice(0, 5)}${text.length > 5 ? "…" : ""}'` : '';
    return `${name}/` + content;
  };

  if (isVisuallyHidden(node)) {
    return {}; // 过滤不可见节点
  }

  const tagName = node.nodeName.toLowerCase();
  tagCounters[tagName] = (tagCounters[tagName] || 0);
  const nodeKey = `${tagName}${tagCounters[tagName]++}`;

  const children = Array.from(node.children)
    .map(child => domTreeToJson(child, tagCounters))
    .filter(childJson => Object.keys(childJson).length > 0); // 去掉空节点

  if (children.length === 0) {
    return { [nodeKey]: getNodeLabel(node) };
  } else {
    const childJson = {};
    children.forEach(child => Object.assign(childJson, child));
    return { [nodeKey]: childJson };
  }
}

function buildDomJsonTree(root = document.body) {
  const topTag = root.nodeName.toLowerCase();
  const result = {};
  result[topTag] = domTreeToJson(root);
  return result;
}

// 用法示例
const domJson = buildDomJsonTree();

// console.log(domJson)
//console.log(JSON.stringify(domJson, null, 2));
return JSON.stringify(domJson, null, 2)

# Database

Structure for data content in pages and articles

## User role

### cms_role
- `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY
- `name` VARCHAR(100) NOT NULL
- `level` TINYINT UNSIGNED NOT NULL

## Articles

### cms_article
- `id` MEDIUMINT UNSIGNED AUTO_INCREMENT PRIMARY KEY
- `url` VARCHAR(1000) NOT NULL
- `publishDateFrom` DATETIME NOT NULL
- `publishDateTo` DATETIME NOT NULL
- `publicate` TINYINT NOT NULL
- `name` VARCHAR(100) NOT NULL
- `preface` TEXT NOT NULL
- `content` TEXT NOT NULL
- `role` INT UNSIGNED NOT NULL (FK to `cms_role.id`)

### cms_article_module
- `id` MEDIUMINT UNSIGNED AUTO_INCREMENT PRIMARY KEY
- `article` MEDIUMINT UNSIGNED (FK to `cms_article.id`)
- `modul` VARCHAR(100) NOT NULL
- `active` TINYINT NOT NULL

### cms_article_module_data
- `module` MEDIUMINT UNSIGNED PRIMARY KEY (FK to `cms_article_module.id`)
- `name` VARCHAR(45) NOT NULL PRIMARY KEY
- `value` TEXT

## Pages

### cms_page
- `id` SMALLINT UNSIGNED AUTO_INCREMENT PRIMARY KEY
- `url` VARCHAR(100) NOT NULL
- `publishDateFrom` DATETIME NOT NULL
- `publishDateTo` DATETIME NOT NULL
- `active` TINYINT NOT NULL
- `role` INT UNSIGNED NOT NULL (FK to `cms_role.id`)

### cms_box
- `id` MEDIUMINT UNSIGNED AUTO_INCREMENT PRIMARY KEY
- `page` SMALLINT UNSIGNED (FK to `cms_article.id`)
- `modul` VARCHAR(100) NOT NULL
- `active` TINYINT NOT NULL

### cms_box_data
- `box` MEDIUMINT UNSIGNED PRIMARY KEY (FK to `cms_box.id`)
- `name` VARCHAR(45) NOT NULL PRIMARY KEY
- `value` TEXT

## SQL queries for data extraction

### Get all articles content
```sql
SELECT a.id, a.url, a.preface, a.content 
FROM cms_article a JOIN cms_role r ON a.role = r.id
WHERE a.publishDateFrom <= NOW() AND (a.publishDateTo IS NULL OR NOW() <= a.publishDateTo) AND a.publicate = 1 AND r.code = 'host';
```

### Get articles with data modules
```sql
SELECT a.id, a.url, d.value
FROM cms_article a
 JOIN cms_role r ON a.role = r.id  AND r.code = 'host'
 JOIN cms_article_module m ON a.id = m.article AND m.modul = 'core/WysiwygModule'
 JOIN cms_article_module_data d ON m.id = d.module AND d.name = 'content'
WHERE a.publishDateFrom <= NOW() AND (a.publishDateTo IS NULL OR NOW() <= a.publishDateTo) AND a.publicate = 1;
```

### Get pages with data modules
```sql
SELECT p.id, p.url, d.value
FROM cms_page p
 JOIN cms_role r ON p.role = r.id  AND r.code = 'host'
 JOIN cms_box b ON p.id = b.page AND b.modul = 'core/WysiwygModule'
 JOIN cms_box_data d ON b.id = d.box AND d.name = 'content'
WHERE p.publishDateFrom <= NOW() AND (p.publishDateTo IS NULL OR NOW() <= p.publishDateTo) AND p.active = 1;
```